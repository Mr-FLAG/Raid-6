import os
import time
from data import DATA_PATH
from src.RAID6 import RAID6

if __name__ == "__main__":

    num_data_disk = 6
    num_check_disk = 2
    chunk_size = 16

    print("Num of Data Disk: " + str(num_data_disk))
    print("Num of Check Disk: " + str(num_check_disk))
    print("Chunk size in bytes: " + str(chunk_size))
    print("\nRAID-6 scheme configuration initialized\n")

    # Initialize RAID6 controller
    controller = RAID6(num_data_disk, num_check_disk, chunk_size)

    # write data objects across storage nodes
    test_obj = 'test.txt'
    raid6_path = os.path.join(DATA_PATH, test_obj)
    # dir: raid6 data stored path
    dir = os.path.join(DATA_PATH, time.strftime('%Y-%m-%d-%H-%M-%S'))
    os.mkdir(dir)
    controller.write_to_disk(raid6_path, dir)

    # choose disk to erase manually
    input_disk = input("choose corrupted disk number (split by space):")
    corrupted_disk = [int(x) for x in input_disk.split()]
    controller.erase_disk(dir, corrupted_disk)

    # rebuild lost redundancy
    controller.rebuild_data(dir, corrupted_disk)
    content = controller.read_from_disk(dir)
    recover_file = "recovered.txt"
    f = open(os.path.join(DATA_PATH, recover_file), 'wb')
    f.write(bytes(content))
    print("Recovered data stored in data/" + recover_file)
