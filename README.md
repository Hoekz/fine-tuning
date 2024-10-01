# Fine Tuning Llama

## Installation

Install the requirements in the `requirements.txt` file.

```sh
pip install -r requirements.txt
```

## Dataset

Use the `dataset.py` script to generate a dataset for training from a codebase.

```sh
python dataset.py ../rfp-assistant 1000 ./dataset
```

## Training

After creating a dataset, train the model using the `train.py` script.

```sh
python train.py ./dataset
```
