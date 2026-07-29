from tests import run_tests, prepare_tests

# You can get all relevant Cultures games here:
#  https://www.gog.com/en/game/cultures_12
#  https://www.gog.com/en/game/cultures_34
#  https://archive.org/details/cultures-saga

# Update paths according to your local files.
games_base_directories = \
    ["C:\\GOG Games\\Cultures and Cultures 2\\Cultures 2",
     "C:\\GOG Games\\Northland and 8th Wonder of the World\\Northland",
     "C:\\GOG Games\\Northland and 8th Wonder of the World\\8th Wonder of the World",
     "C:\\Cultures Saga"]

if __name__ == "__main__":
    prepare_tests(games_base_directories, skip_if_any_test_exists=True)
    run_tests()
