from harmony import Mapper, Experiment

if __name__ == "__main__": 
    data_file = '2017-12-11_B.h5'

    m = Mapper(data_file, name="test")
    m.to_h5()

    ex = Experiment("harmony_root/conformed_data/test.h5")

