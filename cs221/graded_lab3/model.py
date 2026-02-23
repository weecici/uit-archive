import os
import pickle
import tqdm
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.nn.utils.rnn import pack_padded_sequence, pad_packed_sequence

os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")

SEED = 42
torch.manual_seed(SEED)
if torch.cuda.is_available():
    torch.cuda.manual_seed_all(SEED)


def normalize(Sents: list[list[str]], POSs: list[list[str]]):
    for i in range(len(POSs)):
        for j in range(len(POSs[i])):
            if POSs[i][j] == "(":
                POSs[i][j] = "-LRB-"
            elif POSs[i][j] == ")":
                POSs[i][j] = "-RRB-"


class BiLSTM(nn.Module):
    def __init__(
        self,
        vocab_size: int,
        tagset_size: int,
        embedding_dim: int = 128,
        hidden_dim: int = 256,
    ):
        super(BiLSTM, self).__init__()
        assert (
            hidden_dim % 2 == 0
        ), "Hidden dimension must be even for bidirectional LSTM"

        self.embedding = nn.Embedding(vocab_size, embedding_dim, padding_idx=0)
        self.lstm = nn.LSTM(
            embedding_dim,
            hidden_dim,
            num_layers=2,
            bidirectional=False,
            batch_first=True,
            dropout=0.1,
        )
        self.hidden2tag = nn.Linear(hidden_dim, tagset_size)

    def forward(self, x, lengths):

        embeds = self.embedding(x)

        packed_embeds = pack_padded_sequence(
            embeds,
            lengths,
            batch_first=True,
            enforce_sorted=False,
        )

        packed_output, _ = self.lstm(packed_embeds)

        output, _ = pad_packed_sequence(packed_output, batch_first=True)

        logits = self.hidden2tag(output)

        return logits

    def loss(self, logits: torch.Tensor, labels: torch.Tensor) -> torch.Tensor:
        logits = logits.reshape(-1, logits.shape[-1])
        labels = labels.reshape(-1)
        loss = F.cross_entropy(logits, labels, ignore_index=-1)
        return loss


class POSTagger:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        self.token2id = {"<pad>": 0, "<unk>": 1}
        self.tag2id = {"<pad>": -1}
        self.id2tag = {}

        self.lr = 1e-2
        self.min_lr = self.lr / 100
        self.weight_decay = 1e-5
        self.num_epochs = 20
        self.train_batch_size = 512
        self.grad_accum_steps = 1

        self.pred_batch_size = 64

    def process_batch_sents(
        self,
        batch_str_list: list[list[str]],
        str2id: dict[str, int],
    ) -> tuple[torch.Tensor, list[int]]:
        unk_id = str2id.get("<unk>", str2id.get("<pad>", 0))
        batch_ids = [
            [str2id.get(s, unk_id) for s in str_list] for str_list in batch_str_list
        ]

        lengths = [len(ids) for ids in batch_ids]
        max_len = max(lengths)

        padded_ids = torch.full(
            (len(batch_ids), max_len),
            str2id["<pad>"],
            dtype=torch.long,
        )

        for i, ids in enumerate(batch_ids):
            padded_ids[i, : len(ids)] = torch.tensor(ids, dtype=torch.long)

        return padded_ids.to(self.device, non_blocking=True), lengths

    def fit(self, Sents: list[list[str]], POSs: list[list[str]]):

        normalize(Sents, POSs)
        n = len(Sents)

        vocab = sorted({word for sent in Sents for word in sent})
        tagset = sorted({tag for tags in POSs for tag in tags})

        for i, word in enumerate(vocab, start=2):
            self.token2id[word] = i

        for i, tag in enumerate(tagset):
            self.tag2id[tag] = i
            self.id2tag[i] = tag

        self.model = BiLSTM(
            vocab_size=len(self.token2id),
            tagset_size=len(tagset),
        )

        opt = torch.optim.AdamW(
            self.model.parameters(),
            lr=self.lr,
            weight_decay=self.weight_decay,
        )
        sch = torch.optim.lr_scheduler.CosineAnnealingLR(
            opt, T_max=self.num_epochs, eta_min=self.min_lr
        )

        self.model.to(self.device)
        self.model.train()
        for epoch in range(self.num_epochs):
            print(f"\nEpoch {epoch+1}/{self.num_epochs}: LR={sch.get_last_lr()[0]:.6f}")

            indices = torch.randperm(n)
            step = 1
            total_loss = 0.0
            self.model.zero_grad(set_to_none=True)

            for start in tqdm.tqdm(range(0, n, self.train_batch_size)):
                batch_indices = indices[start : start + self.train_batch_size]
                batch_sents = [Sents[i] for i in batch_indices]
                batch_tags = [POSs[i] for i in batch_indices]

                batch_inputs, lengths = self.process_batch_sents(
                    batch_sents, self.token2id
                )
                batch_labels, _ = self.process_batch_sents(batch_tags, self.tag2id)

                logits = self.model(batch_inputs, lengths)
                loss = self.model.loss(logits, batch_labels)
                total_loss += loss.item()
                loss /= self.grad_accum_steps
                loss.backward()

                if (
                    step % self.grad_accum_steps == 0
                    or start + self.train_batch_size >= n
                ):
                    opt.step()
                    self.model.zero_grad(set_to_none=True)

                step += 1

            avg_loss = total_loss / (step - 1)
            print(f"-> Average Loss of Epoch {epoch+1}: {avg_loss:.4f}")

            sch.step()

    def predict(self, Sents: list[list[str]]):
        self.model.to(self.device)
        self.model.eval()
        n = len(Sents)

        preds: list[list[str]] = []
        with torch.no_grad():
            for start in range(0, n, self.pred_batch_size):
                batch_sents = Sents[start : start + self.pred_batch_size]
                batch_inputs, lengths = self.process_batch_sents(
                    batch_sents, self.token2id
                )
                logits = self.model(batch_inputs, lengths)  # (B, T, C)
                pred_ids = logits.argmax(dim=-1).tolist()  # (B, T)

                for seq_pred_ids, length in zip(pred_ids, lengths):
                    seq_tags = [self.id2tag[i] for i in seq_pred_ids[:length]]
                    preds.append(seq_tags)

        return preds

    @staticmethod
    def load(path: str = "model.mdl"):
        return pickle.load(open(path, "rb"))

    def save(self):
        self.device = torch.device("cpu")
        self.model.to(self.device)
        return pickle.dump(self, open("model.mdl", "wb"))
