import numpy as np 

class GaloisField(object):
    '''Galois Field module
    A class that defines foundamental 
    mathematics in RAID6 
    '''
    def __init__(self, num_data_disk, num_check_disk, w = 8, modulus = 0b100011101):
        '''inital setting
        field: GF(2^w), w=8
        primitive polynomial: x^8+x^4+x^3+x^2+1
        '''
        self.num_data_disk = num_data_disk
        self.num_check_disk = num_check_disk
        self.w = w
        self.modulus = modulus
        self.bound = 1 << w
        self.gflog = np.zeros(self.bound, dtype=int)
        self.gfilog = np.zeros(self.bound, dtype=int)
        self.vander = np.zeros((self.num_check_disk, self.num_data_disk), dtype=int)
        self.setup_tables()
        self.setup_vander()
    
    def setup_tables(self):
        '''Set up the look up logarithm table
        '''
        b = 1
        for log in range(self.bound - 1):
            self.gflog[b] = log
            self.gfilog[log] = b
            b = b << 1
            if b & self.bound:
                b = b ^ self.modulus
    
    def setup_vander(self):
        '''Set up the Vandermond matrix
        '''
        for i in range(self.num_check_disk):
            for j in range(self.num_data_disk):
                self.vander[i][j] = self.power(j+1, i)
    
    def add(self, a, b):
        '''Sum in Galosis Field
        '''
        return a ^ b

    def sub(self, a, b):
        '''Subtraction in Galosis Field
        '''
        return a ^ b
    
    def mul(self, a, b):
        '''muliplication in Galosis Field
        :param a: muliplicand
        :param b: muliplier
        '''
        if a == 0 or b == 0:
            return 0 
        sum_log = (self.gflog[a] + self.gflog[b]) % (self.bound - 1)
        return self.gfilog[sum_log]
    
    def div(self, a, b):
        '''Division in Galosis Field
        :param a: dividend
        :param b: divisor
        '''
        if a == 0:
            return 0
        if b == 0:
            raise Exception("Error: Divisor can't be zero.")
        diff_log = (self.gflog[a] - self.gflog[b]) % (self.bound - 1)
        return self.gfilog[diff_log]
    
    def power(self, a, n):
        '''Exponentiation in Galosis Field
        :param a: base
        :param n: exponent
        '''
        n %= self.bound - 1
        res = 1
        for i in range(n):
            res = self.mul(a, res)
        return res

    def dot(self, a, b):
        '''Inner product of vector
        ：param a, b: vectors
        '''
        if len(a) != len(b):
            raise Exception("Error: Vector dot product: Vector length not match.")
        res = 0
        for i in range(len(a)):
            res = self.add(res, self.mul(a[i], b[i]))
        return res

    def matmul(self, a, b):
        '''Matrix muliplication
        :param a, b: matrices
        '''
        if len(a[0]) != len(b):
            raise Exception("Error: Matrix muliplication dimensions not match.")
        res = np.zeros([len(a), len(b[0])], dtype=int)
        for i in range(len(res)):
            for j in range(len(res[0])):
                res[i][j] = self.dot(a[i, :], b[:, j])
        return res

    def inverse(self, A):
        """
        calculate the inverse matrix of A
        :param A: matrix
        """
        if len(A) != len(A[0]):
            raise Exception("Error: Non-square matrix is irreversible.")

        A_ = np.concatenate((A, np.eye(len(A), dtype=int)), axis=1)
        #print(len(A_))
        #print(len(A_[0]))
        '''
        A_: Matrix [A I]
        '''
        dim = len(A_)
        for i in range(dim):
            """Deal with A_[i, i] = 0 - make it non-zero."""
            if A_[i, i] == 0:
                for j in range(i + 1, dim):
                    if A_[j, i] != 0:
                        for k in range(len(A_[i])):
                            A_[i, k] = self.add(A_[i, k], A_[j, k])
                        break

            '''Unitization of present row based on the pivot'''
            pivot = A_[i, i]
            for j in range(len(A_[i])):
                A_[i, j] = self.div(A_[i, j], pivot)

            '''#Gaussian Elimination'''
            for j in range(dim):
                if i != j:
                    proportion = self.div(A_[j, i], A_[i, i])
                    for k in range(i, len(A_[i])):
                        A_[j, k] = self.add(A_[j, k], self.mul(A_[i, k], proportion))
        A_inverse = A_[:, dim:2*dim]

        """last row is 0 - This square matrix is irreversible."""
        if sum(A_[dim-1, 0: dim]) == 0:
                raise Exception("Error: This square matrix is irreversible.")
        return A_inverse