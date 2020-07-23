from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.metrics import classification_report, confusion_matrix
import file_utilities
import json
from sklearn.utils import shuffle
import numpy as np
from pathlib import Path


def load_dataset():
    countries = file_utilities.get_countries()
    dataset = list()
    for country in countries:
        revisions = file_utilities.get_revisions(country)
        text = ""
        for i in range(len(revisions)):
            if i % 10 == 0:
                text += file_utilities.parse_text(revisions[i]["text"])
        dataset.append(text)
        print(len(dataset))
    file_utilities.compressed_pickle("bigdataset", dataset)


if __name__ == "__main__":
    # Loading Dataset
    exists = Path.exists(Path("bigdataset.pbz2"))
    if not exists:
        load_dataset()
    data = file_utilities.decompress_pickle("bigdataset.pbz2")
    # Preprocessing
    print("Preprocessing Dataset")
    with open("ranked_countries.json") as json_file:
        y = json.load(json_file)
    y = [*y.values()]
    # Splitting in Train and Test
    print("Splitting Dataset") # 80/20
    data, y = shuffle(data, y, random_state=42)
    x_train = np.array(data[:164])
    x_test = np.array(data[42:])
    y_train = np.array(y[:164])
    y_test = np.array(y[42:])

    # Vectorization
    vectorizer = TfidfVectorizer(
        sublinear_tf=True,
        min_df=5,
        norm="l2",
        ngram_range=(1, 2),
        stop_words="english",
    )
    print("Starting Vectorization #1")
    x_train = vectorizer.fit_transform(x_train)
    x_test = vectorizer.transform(x_test)

    print("SVC for Multiclass Classification")
    model = LinearSVC(class_weight="balanced").fit(x_train, y_train)
    y_pred = model.predict(x_test)
    print(confusion_matrix(y_test, y_pred))
    print(classification_report(y_test, y_pred))
