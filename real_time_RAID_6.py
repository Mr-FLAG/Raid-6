import os
import time
import math
from data import DATA_PATH
from src.RAID6 import RAID6

if __name__ == "__main__":

    data_root = './data/'
    file_seq = ["63B.txt", "75K.pdf", "786K.jpg", "5M.pdf"]
    log_seq = ["log_63B", "log_75K", "log_786K", "log_5M"]
    file_recover_seq = ["63B_re.txt", "75K_re.pdf", "786K_re.jpg", "5M_re.pdf"]
    chunk_size_seq = [8, 32, 64, 256, 256*1024]
    disk_pair = ["0 1", "2 3", "4 5", "6 7", "0 7"]
    num_data_disk = 6
    num_check_disk = 2
    chunk_size = 8
    strip_size = chunk_size * num_data_disk
    # -----------ST4000VM000 parameter---------
    seek_time = 0.012
    rpm = 5900
    waiting_time = 60/rpm
    dir_time = seek_time + waiting_time
    read_write_rate = 146e6
    #------------------------------------------------
    print("Num of Data Disk: " + str(num_data_disk))
    print("Num of Check Disk: " + str(num_check_disk))
    #print("Chunk size in bytes: "+ str(chunk_size))
    print("RAID-6 scheme configuration initialized")
    if not os.path.exists("log"):
        os.mkdir("log")
    for i in range(len(file_seq)):
        for j in range(len(chunk_size_seq)):
            file_name = file_seq[i]
            chunk_size = chunk_size_seq[j]
            strip_size = chunk_size * num_data_disk
            file_size = os.path.getsize(data_root + file_name)
            num_of_strip = math.ceil(file_size / strip_size)
            total_dir_time = dir_time * num_of_strip
            total_IO_time = file_size/read_write_rate
            print("Chunk size in bytes: " + str(chunk_size))
            print("file size: " + str(file_size))
            write_path = "log/" + log_seq[i] + "_write_" + str(num_data_disk + num_check_disk) + '_' + str(
                chunk_size) + ".txt"
            rebuild_path = "log/" + log_seq[i] + "_rebuild_" + str(num_data_disk + num_check_disk) + '_' + str(
                chunk_size) + ".txt"
            read_path = "log/" + log_seq[i] + "_read_" + str(num_data_disk + num_check_disk) + '_' + str(
                chunk_size) + ".txt"
            write_log = open(write_path, "w")
            rebuild_log = open(rebuild_path, "w")
            read_log = open(read_path, "w")

            # Initialize RAID6 controller
            controller = RAID6(num_data_disk, num_check_disk, chunk_size)
            # write data objects across storage nodes
            raid6_path = os.path.join(DATA_PATH, file_name)
            # dir: raid6 data stored path
            dir = os.path.join(DATA_PATH, file_name + 'chunk' + str(chunk_size) + time.strftime('%Y-%m-%d-%H-%M-%S'))
            os.mkdir(dir)

            # Record write time
            total_parity_time = controller.write_to_disk(raid6_path, dir)
            single_parity_time = total_parity_time / num_of_strip
            single_write_time = dir_time + single_parity_time + total_IO_time/num_of_strip
            total_write_time = dir_time*num_of_strip + total_parity_time + total_IO_time
            write_log.write('total_write_time= ' + str(total_parity_time) + '\n'
                            +'single_write_time= ' + str(single_write_time) + '\n')

            # read time
            read_time = dir_time*num_of_strip + total_IO_time
            read_log.write('read_time= ' + str(read_time)+ '\n')

            # rebuild lost redundancy
            corrupted_disk = [int(x) for x in disk_pair[0].split()]
            controller.erase_disk(dir, corrupted_disk)
            total_rebuild_parity_time = controller.rebuild_data(dir, corrupted_disk)
            rebuild_1_parity_time = total_rebuild_parity_time/num_of_strip
            single_rebuild_time = rebuild_1_parity_time + dir_time + total_IO_time/num_of_strip
            total_rebuild_time = total_rebuild_parity_time + total_dir_time + total_IO_time
            rebuild_log.write('single_rebuild_time= ' + str(single_rebuild_time) + '\n'
                              +'total_rebuild_time= ' + str(total_rebuild_time) + '\n')

        time.sleep(1)
        read_log.close()
        rebuild_log.close()
        write_log.close()
