import os
import time
from data import DATA_PATH
from src.RAID6 import RAID6

if __name__ == "__main__":

    file_seq = ["63B.txt", "75K.pdf", "786K.jpg", "5M.pdf"]
    log_seq = ["log_63B", "log_75K", "log_786K", "log_5M"]
    file_recover_seq = ["63B_re.txt", "75K_re.pdf", "786K_re.jpg", "5M_re.pdf"]
    chunk_size_seq = [8, 16, 32, 64, 128, 256]
    disk_pair = ["0 1", "2 3", "4 5", "6 7", "0 7"]
    num_data_disk = 6
    num_check_disk = 2
    chunk_size = 8

    print("Num of Data Disk: " + str(num_data_disk))
    print("Num of Check Disk: " + str(num_check_disk))
    #print("Chunk size in bytes: "+ str(chunk_size))
    print("RAID-6 scheme configuration initialized")
    if not os.path.exists("log"):
        os.mkdir("log")

    for i in range(4):
        test_obj = file_seq[i]
        if not os.path.exists("log/" + log_seq[i]):
            os.mkdir("log/" + log_seq[i])
        for chunk_size in chunk_size_seq:
            print("Chunk size in bytes: " + str(chunk_size))
            write_path = "log/" + log_seq[i] + "/write_" + str(num_data_disk + num_check_disk) + '_' + str(chunk_size) + "_2.txt"
            rebuild_path = "log/" + log_seq[i] + "/rebuild_" + str(num_data_disk + num_check_disk) + '_' + str(chunk_size) + "_2.txt"
            read_path = "log/" + log_seq[i] + "/read_" + str(num_data_disk + num_check_disk) + '_' + str(chunk_size) + "_2.txt"
            write_log = open(write_path, "a")
            rebuild_log = open(rebuild_path, "a")
            read_log = open(read_path, "a")

            for j in range(5):
                # Initialize RAID6 controller
                controller = RAID6(num_data_disk, num_check_disk, chunk_size)
                # write data objects across storage nodes
                raid6_path = os.path.join(DATA_PATH, test_obj)
                # dir: raid6 data stored path
                dir = os.path.join(DATA_PATH, time.strftime('%Y-%m-%d-%H-%M-%S'))
                os.mkdir(dir)

                #Record write time
                start_time = time.time()
                controller.write_to_disk(raid6_path, dir)
                write_log.write(str(time.time() - start_time) + '\n')

                # choose disk to erase manually
                #input_start_time = time.time()
                #input_disk = input("choose corrupted disk number (split by space):")
                #input_time = time.time() - input_start_time
                corrupted_disk = [int(x) for x in disk_pair[j].split()]
                controller.erase_disk(dir, corrupted_disk)

                # rebuild lost redundancy
                #input("\nPress Enter to rebuild lost data ...\n")
                start_time = time.time()
                controller.rebuild_data(dir, corrupted_disk)
                rebuild_log.write(str(time.time() - start_time) + '\n')

                # read from recovered disk
                start_time = time.time()
                content = controller.read_from_disk(dir)
                read_log.write(str(time.time() - start_time) + '\n')
                recover_file = file_recover_seq[i]
                f = open(os.path.join(DATA_PATH, recover_file), 'wb')
                f.write(bytes(content))
                print("Recovered data stored in data/" + recover_file)
                #print("Program time cost: " + str(end_time - start_time) + "s")
                time.sleep(1)
            read_log.close()
            rebuild_log.close()
            write_log.close()
