# huffman_algorithm

Compressed binary string consists of:
1. header:
   a) count of bytes UTF-8 encoded of rest of header
   b) UTF-8 symbols encoded: '0', '1' or symbol
2. sequence to decode

   For Linux:
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
`
python3 main.py tests/test_files/test2.xml tests/test_files/test2_enc && 
python3 main.py decode tests/test_files/test2_enc tests/test_files/test2_res && 
rm tests/test_files/test2_enc tests/test_files/test2_res
`
--- 189 different symbols ---
--- 1.6713712215423584 seconds to define symbols frequency ---
--- 3.348515033721924 seconds to encode file ---
--- 5.04868221282959 seconds to compress file ---
--- Compression: 55.02 % ---
--- 3.814774751663208 seconds to read all bytes from file ---
--- 6.650456666946411 seconds to decode file and write it to dest ---
--- 10.486353397369385 seconds to decompress ---
--- Compression: 55.02 % ---

`
cat tests/test_files/test2.xml > tests/test_files/test2_tmp.xml && 
cat tests/test_files/test2.xml >> tests/test_files/test2_tmp.xml && 
cat tests/test_files/test2.xml >> tests/test_files/test2_tmp.xml  && 
python3 main.py tests/test_files/test2_tmp.xml tests/test_files/test2_enc && 
python3 main.py decode tests/test_files/test2_enc tests/test_files/test2_res.xml &&
rm tests/test_files/test2_tmp.xml tests/test_files/test2_enc tests/test_files/test2_res.xml
`
--- 189 different symbols ---
--- 5.279628038406372 seconds to define symbols frequency ---
--- 10.481949806213379 seconds to encode file ---
--- 15.796982765197754 seconds to compress file ---
--- Compression: 55.02 % ---
--- 11.384727239608765 seconds to read all bytes from file ---
--- 20.392462968826294 seconds to decode file and write it to dest ---
--- 31.833117961883545 seconds to decompress ---
--- Compression: 55.02 % ---
