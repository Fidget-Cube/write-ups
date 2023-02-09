from pwn import *
from Crypto.Util.strxor import strxor

HOST = 'mc.ax'
PORT = 31497

conn = remote(HOST, PORT)
print(conn.recv().decode())

m0 = '00000000000000000000000000000000\n'
m1 = 'ffffffffffffffffffffffffffffffff\n'

for experiment in range(1, 129):
    # Send an encryption query with 00000000000000000000000000000000 and ffffffffffffffffffffffffffffffff
    conn.send('1\n'.encode())
    conn.recv().decode()
    conn.send(m0.encode())
    conn.recv().decode()
    conn.send(m1.encode())
    ct_a = bytes.fromhex(conn.recv().decode().split('\n')[0])
    ct0_a = ct_a[:256]
    ct1_a = ct_a[256:]

    # Send an encryption query with two 00000000000000000000000000000000s
    conn.send('1\n'.encode())
    conn.recv().decode()
    conn.send(m0.encode())
    conn.recv().decode()
    conn.send(m0.encode())
    ct_b = bytes.fromhex(conn.recv().decode().split('\n')[0])
    ct0_b = ct_b[:256]
    ct1_b = ct_b[256:]

    # Decode ct0_a and ct1_b together (to bypass the decryption check)
    conn.send('2\n'.encode())
    conn.recv().decode()
    conn.send((ct0_a.hex() + ct1_b.hex() + '\n').encode())
    pt_a = bytes.fromhex(conn.recv().decode().split('\n')[0])
    
    # Decode ct0_b and ct1_a together (to bypass the decryption check)
    conn.send('2\n'.encode())
    conn.recv().decode()
    conn.send((ct0_b.hex() + ct1_a.hex() + '\n').encode())
    pt_b = bytes.fromhex(conn.recv().decode().split('\n')[0])

    # pt_a = random_data_a ^ random_data_b
    # pt_b = random_data_a ^ random_data_b ^ (m0|m1)
    # pt_a ^ pt_b = (m0|m1)
    res = strxor(pt_a, pt_b).hex()
    print(res)
    # res is the decrypted plaintext of our first encryption query
    # If res is 00000000000000000000000000000000, we know the bit is 0. If it is ffffffffffffffffffffffffffffffff, we know the bit is 1.

    # Submit the bit
    conn.send('0\n'.encode())
    conn.recv().decode()
    if res == m0.strip():
        conn.send('0\n'.encode())
    elif res == m1.strip():
        conn.send('1\n'.encode())
    else:
        print("error")
        break
    print(conn.recv().decode())


conn.close()
