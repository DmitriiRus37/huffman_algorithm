# huffman_algorithm


1. download project
2. cd /path/to/project
3. `python3 -m venv venv` to create python environment
4. `chmod +x ./venv/bin/activate && ./venv/bin/activate`
5. `pip install -r requirements.txt`
6.                   
   a) `python3 main.py *source_path* *dest_path*` to encode;   
   or   
   b) `python3 main.py decode *source_path* *dest_path*` to decode;

You can check:
`python3 main.py files/test2.xml files/test2_enc && python3 main.py decode files/test2_enc files/res`


Compressed binary string consists of:
1. count of unique symbols (4 bytes)
2. symbols encoding (4 bytes per symbol)
3. symbol codes (4 bytes per code)
4. sequence 



--- 1.2671279907226562 seconds to define symbols frequency ---
--- 2.659576416015625 seconds to encode file ---
--- 3.9388046264648438 seconds to compress file ---
--- 2.7043514251708984 seconds to read all bytes from file ---
--- 4.853003740310669 seconds to decode file and write it to dest ---
--- 7.579028844833374 seconds to decompress ---

 

