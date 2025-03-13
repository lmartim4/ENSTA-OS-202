# How to run the :fire: simulation

```
git clone https://github.com/lmartim4/ENSTA-OS-202.git
python3 -m venv tp_parallel
source tp_parallel/bin/activate
cd projet
pip install -r requirements.txt
mkdir build && cd build && cmake ../ && cd ..
```

In order to start a loop for varying *Open MP threads* and plotting the graphs with python.

```
./run_simulation.sh
```


