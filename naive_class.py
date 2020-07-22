import metrics
import file_utilities as fut
import statistics as stat
import metrics
def naive_classifier():
    countries = fut.get_countries()

    for country in countries:

        revisions = stat.get_revisions(country)
        print(revisions["text"])
        break
if __name__ == "__main__":
    naive_classifier()