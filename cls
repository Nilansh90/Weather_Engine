[33mfd6149d[m[33m ([m[1;36mHEAD[m[33m -> [m[1;32mmain[m[33m, [m[1;31morigin/main[m[33m)[m Apply gitignore and remove ignored files
 .idea/.gitignore                               |    3 [31m-[m
 .idea/Weather_Project.iml                      |    8 [31m-[m
 .idea/inspectionProfiles/Project_Default.xml   |   13 [31m-[m
 .idea/inspectionProfiles/profiles_settings.xml |    6 [31m-[m
 .idea/misc.xml                                 |    7 [31m-[m
 .idea/modules.xml                              |    8 [31m-[m
 .idea/vcs.xml                                  |    6 [31m-[m
 data/latest_forecasts.json                     |  132 [31m-[m
 data/processed/Bangalore/test.csv              |  823 [31m----[m
 data/processed/Bangalore/train.csv             | 3834 [31m-----------------[m
 data/processed/Bangalore/val.csv               |  822 [31m----[m
 data/processed/Delhi/test.csv                  |  823 [31m----[m
 data/processed/Delhi/train.csv                 | 3834 [31m-----------------[m
 data/processed/Delhi/val.csv                   |  822 [31m----[m
 data/processed/Mumbai/test.csv                 |  823 [31m----[m
 data/processed/Mumbai/train.csv                | 3834 [31m-----------------[m
 data/processed/Mumbai/val.csv                  |  822 [31m----[m
 data/processed/Nagpur/test.csv                 |  823 [31m----[m
 data/processed/Nagpur/train.csv                | 3834 [31m-----------------[m
 data/processed/Nagpur/val.csv                  |  822 [31m----[m
 data/processed/Pilani/test.csv                 |  823 [31m----[m
 data/processed/Pilani/train.csv                | 3834 [31m-----------------[m
 data/processed/Pilani/val.csv                  |  822 [31m----[m
 data/raw/Bangalore_history.csv                 | 5477 [31m------------------------[m
 data/raw/Delhi_history.csv                     | 5477 [31m------------------------[m
 data/raw/Mumbai_history.csv                    | 5477 [31m------------------------[m
 data/raw/Nagpur_history.csv                    | 5477 [31m------------------------[m
 data/raw/Pilani_history.csv                    | 5477 [31m------------------------[m
 model/temp_max_model.joblib                    |  Bin [31m6953621[m -> [32m0[m bytes
 model/temp_min_model_chained.joblib            |  Bin [31m5265757[m -> [32m0[m bytes
 model/wind_direction_model_advanced.joblib     |  Bin [31m985396[m -> [32m0[m bytes
 model/wind_speed_tweedie_v1.joblib             |  Bin [31m13451103[m -> [32m0[m bytes
 model/wind_speed_xgboost_v1.joblib             |  Bin [31m32765681[m -> [32m0[m bytes
 33 files changed, 54963 deletions(-)
[33mffc8b10[m Add gitignore
 .gitignore | 122 [32m++++++++++++++++++++++++++++++++++[m[31m---------------------------[m
 1 file changed, 68 insertions(+), 54 deletions(-)
