find . -name '*.iic' | xargs -I xxx -P0 python gen_csv.py xxx
