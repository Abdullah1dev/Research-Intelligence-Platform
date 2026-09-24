import json
from pathlib import Path


#get the project root directory

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Path to evaluation dataset
DATASET_PATH = (
    PROJECT_ROOT
    / "evaluation"
    / "datasets"
    / "research_questions.json"
)


def load_dataset():
    with open(
        DATASET_PATH,
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)
    
    

def main():
    dataset = load_dataset()

    print(f"Loaded {len(dataset)} evaluation questions.\n")

    for item in dataset:
        print(
            f"{item['id']}: "
            f"{item['question']}"
        )


if __name__ == "__main__":
    main()
    