# Learning to simulate: Predicting bioelectric patterns in cells population for morphological control

Bioelectric cell properties strategies aim to develop specific drug interventions for modulating stem cell functionalities, regenerative responses and tumor reprogramming. The understanding and controlling of bioelectric mechanisms have seen considerable progress recently. The recent development of highly detailed and accurate software modelling complex bioelectrical signals provided a first quantitative approach to reverse engineering bioelectric states. Specifically, computational models have been used to identify known ion channel drugs that induce desired bioelectric states in vivo and cause repair of injury, birth defects, and cancer. However, it is important to note that these models involve a large amount of parameters that have to be explored to identify a solution. Taking this into consideration, the accurate simulation could become time-consuming. Here we present a different approach which uses machine learning to build an accurate simulator reducing simulations time by orders of magnitude compared to other approaches. This will enable researchers to explore the large space of bioelectric patterns in order to infer what interventions are responsible for achieving a specific bioelectric pattern. The implications of this work will allow us to derive what interventions can be performed to induce the desired bioelectric states and help researchers accelerate the development of therapeutic solutions for control of regenerative responses, birth defects, and tumor reprogramming.

# Get Started

Before it is necessary to setup a virtual environment
```
mkvirtualenv test
pip install -r requirements.txt
```

The Code can be separated into 4 processes
- **Data Generation Process** (Testing & Debugging): `python3 run.py generate test`
- **Data Preparation Process**: `python3 run.py prepare`
- **Model Training**: Run the [Colab Notebook](https://colab.research.google.com/drive/1Hw2dcvQVyRjUbQotlwMJ8QVSQ8eRdCr9?usp=sharing) & Download the trained model.pth in `storage/model_v${versionNumber}`. Important that you name the trained model file as *model_v${versionNumber}*
- **Results Analysis**: `python3 run.py visualize`. Before running the command, update `analysis/__init__.py` line 20 with `${versionName}`. Results will be available in folder `analysis/data_v${versionName}`

