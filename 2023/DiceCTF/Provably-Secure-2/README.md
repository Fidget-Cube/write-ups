# Provably Secure 2
## Now with less cheese! Still pretty simple though. `nc mc.ax 31497`
> category: Crypto  
> author: jyu  
> solves: 155  
> points: 117  
> challenge file(s): [server.py](https://github.com/Fidget-Cube/write-ups/tree/main/2023/DiceCTF/Provably-Secure-2/server.py)  
> solution file(s): [client.py](https://github.com/Fidget-Cube/write-ups/tree/main/2023/DiceCTF/Provably-Secure-2/client.py)  


This server is basically a simulation of the IND-CCA2 game testing a custom cryptographic system. The game is described in detail here https://en.wikipedia.org/wiki/Ciphertext_indistinguishability.  

The server makes 128 passes, generating a random bit (0 or 1) each pass. Our goal is to call a "Solve" function, and correctly "guess" the bit 128 times, at which point a flag is printed. In addition, the server also provides "Query Encryption" and "Query Decryption" functions.  
The "Query Encryption" Function asks for 2 messages to encrypt. If the random bit is 0 it encrypts the first one and returns the ciphertext, and if the bit is 1 it encrypts the second. Unfortunately, we are unable to predict this bit using encryption alone, since this cryptosystem is IND-CPA secured. That is, when the cryptosystem is given the same message multiple times, it will encrypt it differently every time. We cannot simply work backwards by comparing ciphertext with their respective plaintext.  
The "Query Decryption" Function takes an encrypted message and decrypts it. Unlike in Provably Secure (original), we can't simply query decryption on ciphertext we just encrypted, which would immediately tell us what message produced the ciphertext. The function checks our input to make sure it doesn't match past encryption queries.  

So we can't cheese this game. We have to prove that this cryptosystem is not IND-CCA2 secured somehow.  

The encryption process uses 2 RSA public/private keys (r0, r1), and goes something like this:  
 - ciphertext = r0-public-key(random_data) + r1-public-key(plaintext ⊕ random_data)  
And the decryption process (with ciphertext split in half):  
 - plaintext = r0-private-key(ciphertext0) ⊕ r1-private-key(ciphertext1)  
This operation works because of properties of the XOR (⊕) operation. Namely, if a ⊕ b = c, then c ⊕ b = a and c ⊕ a = b. We can actually use this property to our advantage.  

Let's make 2 encryption queries. For the first, we'll make m0 00000000000000000000000000000000 for simplicity, and m1 ffffffffffffffffffffffffffffffff for fun.  
```
m0 (16 byte hexstring): 00000000000000000000000000000000
m1 (16 byte hexstring): ffffffffffffffffffffffffffffffff
298c7e2c...
```  
For the second, we'll make both messages the same (also 00000000000000000000000000000000 for simplicity).  
```
m0 (16 byte hexstring): 00000000000000000000000000000000
m1 (16 byte hexstring): 00000000000000000000000000000000
7f5b2a85...
```  
From what we know about the encryption process, both of these outputs are a combination of 2 ciphertexts, I'll name them ct0_a and ct1_a from our first query, and ct0_b and ct1_b from our second. For the rest of this proof, "a" will denote data from our first encryption query, and "b" will denote the second.  
Since these ciphertexts are encrypted and decrypted separately, we can mix them around. What if we were to pair ct0_a with ct1_b, and ct0_b with ct1_a?  
 - r0-private-key(ct0_a) ⊕ r1-private-key(ct1_b) = (random_data_a) ⊕ (plaintext_b ⊕ random_data_b)
 - r0-private-key(ct0_b) ⊕ r1-private-key(ct1_a) = (random_data_b) ⊕ (plaintext_a ⊕ random data_a)
When we made the second query before, we made sure that plaintext_b was 00000000000000000000000000000000 for a reason. Any bit XOR-ed with 0 is itself, the identity property. For this reason, we can remove plaintext_b from the expression, as it does not affect the final XOR product.  
 - random_data_a ⊕ random_data_b
 - random_data_b ⊕ plaintext_a ⊕ random data_a
Using the other property of XOR we know about, we can simply XOR these two values together, and the result will be plaintext_a.  
 - random_data_a ⊕ random_data_b ⊕ random_data_b ⊕ plaintext_a ⊕ random data_a = plaintext_a
And we've successfully recovered plaintext from a ciphertext message! If plaintext_a is 00000000000000000000000000000000, we know m0 was used to make the ciphertext, meaning the random bit is 0. If plaintext_a is ffffffffffffffffffffffffffffffff, the inverse is true, and the random bit is 1.  

