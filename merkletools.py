import hashlib
import binascii
import codecs
try:
    #import sha3
    from hashlib import sha3_256
except:
    from warnings import warn
    warn("sha3 is not working!")


class MerkleTools(object):
    def __init__(self, hash_type="sha256"):
        hash_type = hash_type.lower()
        if hash_type in ['sha256', 'md5', 'sha224', 'sha384', 'sha512',
                         'sha3_256', 'sha3_224', 'sha3_384', 'sha3_512']:
            self.hash_function = getattr(hashlib, hash_type)
        else:
            raise Exception('`hash_type` {} nor supported'.format(hash_type))

        self.reset_tree()

    def _to_hex(self, x):
        try:  # python3
            return x.hex()
        except:  # python2
            return binascii.hexlify(x)

    def reset_tree(self):
        self.leaves = list()
        self.levels = None
        self.is_ready = False

    def add_leaf(self, values, do_hash=False):
        self.is_ready = False
        # check if single leaf
        if not isinstance(values, tuple) and not isinstance(values, list):
            values = [values]
        for v in values:
            if do_hash:
                v = v.encode('utf-8')
                v = self.hash_function(v).hexdigest()
            v = bytearray.fromhex(v)
            self.leaves.append(v)

    def get_leaf(self, index):
        return self._to_hex(self.leaves[index])

    def get_leaf_count(self):
        return len(self.leaves)

    def get_tree_ready_state(self):
        return self.is_ready

    def _calculate_next_level(self):
        solo_leave = None
        N = len(self.levels[0])  # number of leaves on the level
        if N % 2 == 1:  # if odd number of leaves on the level
            solo_leave = self.levels[0][-1]
            N -= 1

        new_level = []
        for l, r in zip(self.levels[0][0:N:2], self.levels[0][1:N:2]):
            new_level.append(self.hash_function(l+r).digest())
        if solo_leave is not None:
            new_level.append(solo_leave)
        self.levels = [new_level, ] + self.levels  # prepend new level

    def make_tree(self):
        self.is_ready = False
        if self.get_leaf_count() > 0:
            self.levels = [self.leaves, ]
            while len(self.levels[0]) > 1:
                self._calculate_next_level()
        self.is_ready = True

    def get_merkle_root(self):
        if self.is_ready:
            if self.levels is not None:
                return self._to_hex(self.levels[0][0])
            else:
                return None
        else:
            return None

    def get_proof(self, index):
        if self.levels is None:
            return None
        elif not self.is_ready or index > len(self.leaves)-1 or index < 0:
            return None
        else:
            proof = []
            for x in range(len(self.levels) - 1, 0, -1):
                level_len = len(self.levels[x])
                if (index == level_len - 1) and (level_len % 2 == 1):  # skip if this is an odd end node
                    index = int(index / 2.)
                    continue
                is_right_node = index % 2
                sibling_index = index - 1 if is_right_node else index + 1
                sibling_pos = "left" if is_right_node else "right"
                sibling_value = self._to_hex(self.levels[x][sibling_index])
                proof.append({sibling_pos: sibling_value})
                index = int(index / 2.)
            return proof

    def validate_proof(self, proof, target_hash):
        target_hash = bytearray.fromhex(target_hash)
        if len(proof) == 0:
            print(target_hash)
            return target_hash
        else:
            proof_hash = target_hash
            for p in proof:
                try:
                    # the sibling is a left node
                    sibling = bytearray.fromhex(p['left'])
                    proof_hash = self.hash_function(sibling + proof_hash).digest()
                except:
                    # the sibling is a right node
                    sibling = bytearray.fromhex(p['right'])
                    proof_hash = self.hash_function(proof_hash + sibling).digest()
            # codecs.decode(proof_hash, 'hex_codec')
            # proof_hash = proof_hash.decode('hex')
            print(proof_hash)
            return proof_hash.hex()