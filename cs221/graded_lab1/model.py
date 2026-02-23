"""
Name: Nguyễn Chí Cường
Student ID: 23520199
-- Powered by Github Copilot:) --
"""

import re
import html
import numpy as np
import nltk
from functools import lru_cache
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import FeatureUnion, Pipeline
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import StandardScaler
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import TweetTokenizer

nltk.download("vader_lexicon")
nltk.download("stopwords")
nltk.download("wordnet")
nltk.download("averaged_perceptron_tagger")
nltk.download("averaged_perceptron_tagger_eng")


_tweet_tok = TweetTokenizer(preserve_case=False, reduce_len=True, strip_handles=True)
lemmatizer = WordNetLemmatizer()
TAG_MAP = {"J": wordnet.ADJ, "V": wordnet.VERB, "N": wordnet.NOUN, "R": wordnet.ADV}
MENTION_TOKEN = "<MENTION>"
URL_TOKEN = "<URL>"

words_dict = {}


def clean_text(texts):
    cleaned_texts = []
    for i, text in enumerate(texts):
        text = html.unescape(text)
        text = re.sub(r"http\S+", f" {URL_TOKEN} ", text)
        text = re.sub(r"@[\w_]+", f" {MENTION_TOKEN} ", text)
        text = re.sub(r"\bRT\b", "", text)
        text = re.sub(r"\s+", " ", text).strip()
        text = re.sub(r'^[\'"`“”‘’]+', "", text).strip()
        cleaned_texts.append(text)
    return cleaned_texts


@lru_cache(maxsize=30000)
def get_lemma(word, tag):
    w_tag = TAG_MAP.get(tag[0], wordnet.NOUN)
    return lemmatizer.lemmatize(word, w_tag)


@lru_cache(maxsize=10000)
def _tokenize_and_lemmatize(text):
    tokens = _tweet_tok.tokenize(text)
    if not tokens:
        return []
    pos_tags = nltk.pos_tag(tokens)
    return [get_lemma(word, tag) for word, tag in pos_tags]


def lemmatize_to_string(text):
    return " ".join(_tokenize_and_lemmatize(text))


class TextStatFeatures(BaseEstimator, TransformerMixin):
    def __init__(self):
        self.sid = SentimentIntensityAnalyzer()

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        features = []

        profanity = {
            "fuck",
            "shit",
            "ass",
            "bastard",
            "motherfucker",
            "mf",
            "dick",
            "pussy",
            "bitch",
            "hoe",
            "slut",
            "whore",
            "cunt",
        }
        identity_slurs = {
            "nigger",
            "nigga",
            "faggot",
            "dyke",
            "tranny",
            "beaner",
            "spic",
            "kike",
            "chink",
            "gook",
            "cracker",
            "queer",
            "retard",
            "fag",
            "coon",
            "cripple",
            "mongoloid",
        }

        violence = {"kill", "die", "murder", "rape", "beat", "shoot"}

        # Sexual/explicit terms (a subset overlaps with profanity but tracked separately)
        sexual_terms = {
            "pussy",
            "pussies",
            "dick",
            "dicks",
            "tits",
            "boobs",
            "boob",
            "cum",
            "blowjob",
            "blowjobs",
            "handjob",
            "handjobs",
            "anal",
            "fuck",
            "fucking",
            "fucked",
        }

        # Identity mentions that are not always slurs but indicate group targeting context
        identity_mentions = {
            "black",
            "blacks",
            "white",
            "whites",
            "mexican",
            "mexicans",
            "asian",
            "asians",
            "jew",
            "jews",
            "jewish",
            "muslim",
            "muslims",
            "christian",
            "christians",
            "arab",
            "arabs",
            "gay",
            "gays",
            "lesbian",
            "lesbians",
            "trans",
            "transgender",
        }

        negations = {"no", "not", "never", "none", "nobody", "nothing", "n't"}

        racist_strong = {
            "nigger",
            "niggers",
            "coon",
            "coons",
            "beaner",
            "beaners",
            "spic",
            "spics",
            "kike",
            "kikes",
            "chink",
            "chinks",
            "gook",
            "gooks",
            "cracker",
            "crackers",
            "wetback",
            "wetbacks",
            "jungle bunny",
            "jungle bunnies",
            "porch monkey",
            "porch monkeys",
            "sand nigger",
            "sand niggers",
            "towel head",
            "towel heads",
            "rag head",
            "rag heads",
        }

        homophobic_strong = {
            "faggot",
            "faggots",
            "fag",
            "fags",
            "dyke",
            "dykes",
            "tranny",
            "trannies",
            "queer",
            "queers",
            "sodomite",
            "sodomites",
        }

        disability_strong = {
            "retard",
            "retards",
            "cripple",
            "cripples",
            "mongoloid",
            "mongoloids",
        }

        severe_slurs = racist_strong | homophobic_strong | disability_strong
        misogynistic_words = {"bitch", "hoe", "slut", "whore", "cunt", "pussy"}

        emoji_pattern = re.compile(
            "["
            "\U0001f600-\U0001f64f"  # Emoticons
            "\U0001f300-\U0001f5ff"  # Symbols & pictographs
            "\U0001f680-\U0001f6ff"  # Transport & map symbols
            "\U0001f1e0-\U0001f1ff"  # Flags
            "\U00002700-\U000027bf"  # Dingbats
            "\U0001f900-\U0001f9ff"  # Supplemental Symbols & Pictographs
            "\U00002600-\U000026ff"  # Misc symbols
            "]+",
            flags=re.UNICODE,
        )

        elong_re = re.compile(r"(.)\1{2,}")

        vader_lex = self.sid.lexicon

        def count_syllables(word):
            word = word.lower()
            count = 0
            vowels = "aeiouy"
            if not word:
                return 0
            if word[0] in vowels:
                count += 1
            for index in range(1, len(word)):
                if word[index] in vowels and word[index - 1] not in vowels:
                    count += 1
            if word.endswith("e"):
                count -= 1
            if count == 0:
                count += 1
            return count

        for text in X:
            s = str(text)
            s_lower = s.lower()
            # Quoted segments
            quoted_spans = re.findall(r"\"([^\"]+)\"|“([^”]+)”|‘([^’]+)’|'([^']+)'", s)
            quoted_texts = [q for group in quoted_spans for q in group if q]

            # Structural features
            num_exclamations = s.count("!")
            num_questions = s.count("?")
            num_ellipses = s.count("...")
            num_hashtags = s.count("#")
            num_mentions = s.count(MENTION_TOKEN)
            num_urls = s.count(URL_TOKEN)

            tokens = _tweet_tok.tokenize(s)
            tok_lower = [t.lower() for t in tokens]
            length = len(tok_lower)

            # RT payload analysis: split at ' : ' after handle if present
            if s.strip().lower().startswith("rt "):
                # try to find first colon which separates RT header from payload
                m = re.search(r":\s", s)
                if m:
                    payload = s[m.end() :]
                    header = s[: m.start()]
                    pl_tokens = _tweet_tok.tokenize(payload.lower())

            # Sentence segmentation (simple): split on ., !, ? for imperative detection
            sentences = re.split(r"[.!?]+\s*", s_lower)

            # All-caps words (length>1)
            num_caps = sum(1 for w in tokens if w.isupper() and len(w) > 1)
            caps_ratio = num_caps / max(1, length)

            # Lexicon counts
            prof_cnt = sum(1 for t in tok_lower if t in profanity)
            slur_cnt = sum(1 for t in tok_lower if t in identity_slurs)
            viol_cnt = sum(1 for t in tok_lower if t in violence)
            neg_cnt = sum(1 for t in tok_lower if t in negations)
            sex_cnt = sum(1 for t in tok_lower if t in sexual_terms)
            ident_mention_cnt = sum(1 for t in tok_lower if t in identity_mentions)

            # Repetition/elongation
            elong_cnt = sum(1 for t in tok_lower if elong_re.search(t))

            # Laughter markers
            lol_cnt = sum(1 for t in tok_lower if t in {"lol", "lmao", "rofl"})

            # Emoji
            emoji_cnt = len(emoji_pattern.findall(s))

            # Diversity/length ratios
            unique_ratio = (len(set(tok_lower)) / max(1, length)) if length else 0.0

            # Readability
            num_syllables = sum(count_syllables(w) for w in tok_lower)
            num_sentences = max(1, s.count(".") + s.count("!") + s.count("?"))
            if length > 0:
                fk_grade = (
                    0.39 * (length / num_sentences)
                    + 11.8 * (num_syllables / length)
                    - 15.59
                )
            else:
                fk_grade = 0.0

            # Word length stats
            num_long_words = sum(1 for t in tok_lower if len(t) > 6)
            num_short_words = sum(1 for t in tok_lower if len(t) < 3)

            # Sentiment interaction
            ss = self.sid.polarity_scores(s)
            neg_score = ss["neg"]
            prof_x_neg = prof_cnt * neg_score
            slur_x_neg = slur_cnt * neg_score

            # Quoted-positivity flip: positive words inside quotes with negative neighborhood
            positive_words = {"beautiful", "love", "truth", "nice", "great", "good"}
            quoted_pos_cnt = 0
            for qt in quoted_texts:
                qt_tokens = _tweet_tok.tokenize(qt.lower())
                if any(w in positive_words for w in qt_tokens):
                    quoted_pos_cnt += 1
            quoted_pos_x_neg = quoted_pos_cnt * neg_score

            # Patterns
            you_are_neg_cnt = 0

            homophobic_cnt = sum(1 for t in tok_lower if t in homophobic_strong)
            disability_cnt = sum(1 for t in tok_lower if t in disability_strong)

            nigger_cnt = sum(1 for t in tok_lower if t in {"nigger", "niggers"})
            nigga_cnt = sum(1 for t in tok_lower if t in {"nigga", "niggas"})
            faggot_cnt = sum(
                1 for t in tok_lower if t in {"faggot", "faggots", "fag", "fags"}
            )

            # Animal slurs in context
            animal_slurs = {"monkey", "monkeys", "ape", "apes", "gorilla", "gorillas"}
            animal_slur_cnt = 0
            if any(t in animal_slurs for t in tok_lower):
                if any(
                    t in {"black", "nigger", "nigga", "niggers", "niggas"}
                    for t in tok_lower
                ):
                    animal_slur_cnt = 1

            # All caps slur
            all_caps_slur_cnt = sum(
                1 for t in tokens if t.isupper() and t.lower() in severe_slurs
            )

            # Phrase features
            bad_bitch_cnt = s_lower.count("bad bitch")
            my_nigga_cnt = s_lower.count("my nigga") + s_lower.count("ma nigga")

            multi_word_slurs = [
                "white trash",
                "porch monkey",
                "sand nigger",
                "towel head",
                "rag head",
            ]
            multi_word_slur_cnt = sum(s_lower.count(slur) for slur in multi_word_slurs)

            # Is a [Slur]
            is_a_slur_cnt = 0
            for i in range(len(tok_lower) - 2):
                if tok_lower[i] in {"is", "are", "be"}:
                    if tok_lower[i + 1] in {"a", "an", "the"}:
                        if (
                            tok_lower[i + 2] in severe_slurs
                            or tok_lower[i + 2] in misogynistic_words
                        ):
                            is_a_slur_cnt += 1
                    elif (
                        tok_lower[i + 1] in severe_slurs
                        or tok_lower[i + 1] in misogynistic_words
                    ):
                        is_a_slur_cnt += 1

            # Context windows: slur/profanity near identity mentions and pronouns
            window = 2
            ident_near_prof_cnt = 0
            for i, t in enumerate(tok_lower):
                if t in {"you", "u", "ur", "you're", "ya"}:
                    start = max(0, i - window)
                    end = min(len(tok_lower), i + window + 1)
                if t in identity_mentions:
                    start = max(0, i - window)
                    end = min(len(tok_lower), i + window + 1)
                    if any(tok_lower[j] in profanity for j in range(start, end)):
                        ident_near_prof_cnt += 1

            for i in range(len(tok_lower)):
                t = tok_lower[i]

                # You are [Negative] / You [Negative]
                if t in {"you", "u", "ya"}:
                    if i + 1 < len(tok_lower):
                        t2 = tok_lower[i + 1]
                        if t2 in {"are", "r", "re", "be"}:
                            if i + 2 < len(tok_lower):
                                t3 = tok_lower[i + 2]
                                if t3 in vader_lex and vader_lex[t3] < -0.5:
                                    you_are_neg_cnt += 1
                        elif t2 in vader_lex and vader_lex[t2] < -0.5:  # "you idiot"
                            you_are_neg_cnt += 1
                elif t in {"you're", "ure", "your", "ur"}:
                    if i + 1 < len(tok_lower):
                        t2 = tok_lower[i + 1]
                        if t2 in vader_lex and vader_lex[t2] < -0.5:
                            you_are_neg_cnt += 1

            dyke_cnt = sum(1 for t in tok_lower if t in {"dyke", "dykes"})
            beaner_cnt = sum(1 for t in tok_lower if t in {"beaner", "beaners"})

            features.append(
                [
                    num_exclamations,
                    num_questions,
                    num_ellipses,
                    num_hashtags,
                    num_mentions,
                    num_urls,
                    caps_ratio,
                    prof_cnt,
                    slur_cnt,
                    viol_cnt,
                    neg_cnt,
                    sex_cnt,
                    ident_mention_cnt,
                    elong_cnt,
                    lol_cnt,
                    emoji_cnt,
                    unique_ratio,
                    fk_grade,
                    num_long_words,
                    num_short_words,
                    prof_x_neg,
                    slur_x_neg,
                    quoted_pos_x_neg,
                    you_are_neg_cnt,
                    nigger_cnt,
                    nigga_cnt,
                    faggot_cnt,
                    bad_bitch_cnt,
                    my_nigga_cnt,
                    multi_word_slur_cnt,
                    homophobic_cnt,
                    disability_cnt,
                    animal_slur_cnt,
                    all_caps_slur_cnt,
                    is_a_slur_cnt,
                    dyke_cnt,
                    beaner_cnt,
                    ident_near_prof_cnt,
                    ss["neg"],
                    ss["neu"],
                    ss["pos"],
                    ss["compound"],
                ]
            )
        return np.array(features, dtype=float)


class model:
    def __init__(self):

        self.seed = 42

        self.vectorizer = FeatureUnion(
            [
                (
                    "word_vectors",
                    TfidfVectorizer(
                        ngram_range=(1, 2),
                        tokenizer=_tokenize_and_lemmatize,
                        min_df=2,
                        max_df=0.95,
                        lowercase=False,
                        sublinear_tf=True,
                        strip_accents="unicode",
                    ),
                ),
                (
                    "char_vectors",
                    TfidfVectorizer(
                        analyzer="char_wb",
                        ngram_range=(3, 3),
                        min_df=4,
                        max_df=0.95,
                        lowercase=False,
                        sublinear_tf=True,
                        strip_accents="unicode",
                    ),
                ),
                (
                    "text_stats_features",
                    Pipeline(
                        [
                            ("stats", TextStatFeatures()),
                            ("scaler", StandardScaler()),
                        ]
                    ),
                ),
            ]
        )

        self.clf = LogisticRegression(
            random_state=self.seed,
            solver="liblinear",
            multi_class="ovr",
            class_weight="balanced",
            C=1.75,
            max_iter=1000,
            tol=1e-8,
        )

    def fit(self, XTrain, YTrain):
        XTrain_cleaned = clean_text(XTrain)
        XTrain_transformed = self.vectorizer.fit_transform(XTrain_cleaned)
        print("Transformed XTrain shape:", XTrain_transformed.shape)
        self.clf.fit(XTrain_transformed, YTrain)

    def predict(self, XTest):
        XTest_cleaned = clean_text(XTest)
        XTest_transformed = self.vectorizer.transform(XTest_cleaned)
        y_pred = self.clf.predict(XTest_transformed)
        return y_pred
