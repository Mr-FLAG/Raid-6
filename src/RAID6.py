import os
import numpy as np
import math
from src.gfield import GaloisField

class RAID6(object):
    '''
    A class for RAID6 controller
    '''
    def __init__(self, num_data_disk, num_check_disk, chunk_size, ram_size, file_dir):
        self.num_data_disk = num_data_disk
        self.num_check_disk = num_check_disk
        self.num_disk = self.num_data_disk + self.num_check_disk
        self.chunk_size = chunk_size
        self.stripe_size = self.num_data_disk * self.chunk_size
        self.gf = GaloisField(num_data_disk = self.num_data_disk,
                              num_check_disk = self.num_check_disk)

        self.data_disk_list = list(range(self.num_data_disk))
        self.check_disk_list = list(range(self.num_data_disk,
                                          self.num_data_disk+self.num_check_disk))
        # added environment variables
        self.ram_size = ram_size
        self.file_dir = file_dir
        self.batch = math.floor(self.ram_size/self.stripe_size)

        if self.batch < 1:
            raise Exception("ram_size has to be larger than the strip size (batch size * num_data_disk)")

        print("controller activated, ready to store data\n")
        #input("Press Enter to continue ...\n")

    def read_data(self, filename, mode = 'rb'):
        f = open(filename, mode)
        return list(f.read())

    
    def distribute_data(self, filename):
        '''split data to different disk
        :param filename:
        :return: data array
        '''
        content = self.read_data(filename)
        self.content_length = len(content)
        file_size = len(content)
        #print(file_size)
        # Total pieces of data segment
        num_of_pieces = math.ceil(file_size / self.stripe_size)
        # Total capacity of data
        total_capacity = num_of_pieces * self.stripe_size
        # print("total capacity: " + str(total_capacity))
        # Not full? zero-padding
        content = content + [0] * (total_capacity - file_size)
        content = np.asarray(content, dtype=int)
        # data matrix
        content = content.reshape(self.num_data_disk,
                                  self.chunk_size * num_of_pieces)
        #print(content.shape[0])
        #print(content.shape[1])
        return content
    
    def compute_parity(self, content):
        '''compute parity based on current data words
        :param content: data words
        :return: checksum words
        '''
        return self.gf.matmul(self.gf.vander, content)
    
    def write_to_disk(self, filename, dir):
        '''concurrently write data and checksum words to each disk
        :param filename:
        :param dir:
        :return:
        '''
        data = self.distribute_data(filename)
        parity = self.compute_parity(data)
        data_with_parity = np.concatenate([data, parity], axis=0)
        for i in range(self.num_disk):
            f = open(os.path.join(dir, 'disk_' + str(i)), 'wb')
            stream_write = bytes(data_with_parity[i, :].tolist())
            f.write(stream_write)
        print("write data and parity to disk successfully\n")
    
    def read_from_disk(self, dir):
        '''read data from each disk
        :param dir: disk directory

        '''
        content = []
        for i in range(self.num_data_disk):
            f = open(os.path.join(dir, 'disk_' + str(i)), 'rb')
            content += list(f.read())
        # No zero-padding content
        content = content[:self.content_length]
        
        return content
       
    def erase_disk(self, dir, erase_list):
        """
        erase the disks
        :param erase_list: disks to be erased
        """
        for i in erase_list:
            os.remove(os.path.join(dir, 'disk_' + str(i)))
            print("\ndisk " + str(i) + " is corrupted(deleted)")

    def rebuild_data(self, dir, corrupted_disk_list):
        '''rebuild data from corrupted disk
        :param dir: disk directory
        :param corrupted_disk_list: corrupted disk
        '''

        if len(corrupted_disk_list) > self.num_check_disk:
            raise Exception("failed to rebuild data due to excessive corrupted disks")

        left_data = []
        left_parity = []
        left_data_disk = list(set(self.data_disk_list).difference(set(corrupted_disk_list)))
        left_check_disk= list(set(self.check_disk_list).difference(set(corrupted_disk_list)))

        for i in left_data_disk:
            left_data.append(self.read_data(os.path.join(dir, 'disk_' + str(i))))

        loop = 0
        num_of_sup = len(corrupted_disk_list)
        #print(num_of_sup)
        #If not enough corrupted disks, to keep check_disk must be decreased.
        for j in left_check_disk:
            if loop < num_of_sup:
                left_parity.append(self.read_data(os.path.join(dir, 'disk_' + str(j))))
                loop += 1

        A = np.concatenate([np.eye(self.num_data_disk, dtype=int), self.gf.vander], axis=0)
        #delete corrupted disks' corresponding matrix rows
        A_= np.delete(A, obj=corrupted_disk_list, axis=0)
        # If corrupted disk is not enough, the matrix A_ will have more rows than columns
        # We need to modify A_ to be square matrix
        while (len(A_) > len(A_[0])):
            A_= np.delete(A_, len(A_)-1, axis=0)

        # left_parity can be null
        E_ = np.asarray(left_data)
        if num_of_sup > 0:
            E_ = np.concatenate([E_, np.asarray(left_parity)], axis=0)

        D = self.gf.matmul(self.gf.inverse(A_), E_)
        C = self.gf.matmul(self.gf.vander, D)

        E = np.concatenate([D, C], axis=0)

        for i in corrupted_disk_list:
            f = open(os.path.join(dir, 'disk_' + str(i)), 'wb')
            to_write = bytes(E[i, :].tolist())
            f.write(to_write)
        
        print("rebuild data successfully\n")