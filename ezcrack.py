import argparse
import glob
import sys
import os

banner = """
                                                            oooo        
                                                            `888        
 .ooooo.    oooooooo  .ooooo.  oooo d8b  .oooo.    .ooooo.   888  oooo  
d88' `88b  d'""7d8P  d88' `"Y8 `888""8P `P  )88b  d88' `"Y8  888 .8P'   
888ooo888    .d8P'   888        888      .oP"888  888        888888.    
888    .o  .d8P'  .P 888   .o8  888     d8(  888  888   .o8  888 `88b.  
`Y8bod8P' d8888888P  `Y8bod8P' d888b    `Y888""8o `Y8bod8P' o888o o888o 
                                                                        
"""

script_dir = str(os.path.dirname(__file__))

def get_rule_lists():

    rulelist_arr = []
    rulelist_arr_no_ext = []

    # read all files not dirs into rulelist_arr
    for filename in glob.iglob(script_dir + '/rules/' + '**/**', recursive=True):
        if os.path.isfile(filename):
            rulelist_arr.append(filename)

    # trim the strings down to just the filename
    for rl in rulelist_arr:
        rl = rl[rl.rindex('/')+1:]
        if rl.find('.') != -1: # check to make sure there is a period in the file name to prevent errors
            rulelist_arr_no_ext.append(rl[:rl.rindex('.')])
        else:
            rulelist_arr_no_ext.append(rl)

    return rulelist_arr,rulelist_arr_no_ext

def get_word_lists():

    wordlist_arr = []
    wordlist_arr_no_ext = []

    # read all files not dirs into wordlist_arr
    for filename in glob.iglob(script_dir + '/wordlists/' + '**/**', recursive=True):
        if os.path.isfile(filename):
         wordlist_arr.append(filename)

    # trim the strings down to just the filename
    for wl in wordlist_arr:
        wl = wl[wl.rindex('/')+1:]
        if wl.find('.') != -1: # check to make sure there is a period in the file name to prevent errors
            wordlist_arr_no_ext.append(wl[:wl.rindex('.')])
        else:
            wordlist_arr_no_ext.append(wl)

    return wordlist_arr,wordlist_arr_no_ext

def check_if_dirs_exist():
    if os.path.isdir(script_dir + "/wordlists") == False:
        os.makedirs(script_dir + "/wordlists")

    if os.path.isdir(script_dir + "/rules") == False:
        os.makedirs(script_dir + "/rules")


if __name__ == '__main__':

    print(banner)

    #check if os is linux
    if sys.platform != "linux":
        printnlog("[!] This program is Linux only")
        exit(1)

    #if the ./wordlists and ./rules dirs dont exist create them
    check_if_dirs_exist()

    #pull the lists from the dirs
    wordlist_full, wordlist_args = get_word_lists()
    rulelist_full, rulelist_args = get_rule_lists()

    parser = argparse.ArgumentParser(add_help=True, description="A wrapper for hashcat to make pentesting easier")

    parser.add_argument('infile', action='store', help='File of hashes to crack')

    wordlist_args.append('ALL')
    parser.add_argument('-w', action='store', choices=wordlist_args, required=True, help='Wordlist files to use found in {}/wordlists/'.format(script_dir))

    #rulelist_args.append('ALL')
    parser.add_argument('-r', action='store', choices=rulelist_args, help='Rule files to use found in {}/rules/'.format(script_dir))

    parser.add_argument('-m', action='store', choices=['netNTLMv1', 'netNTLMv2', 'kerberoast', 'asreproast', 'dcc2'], default='netNTLMv2', help='Type of hash you want to crack')
    parser.add_argument('-o', action='store', help='File to output hashes to')
    parser.add_argument('-s', action='store_true', help='Auto shutdown upon completion')

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    options = parser.parse_args()

    if len(wordlist_full) < 1:
        print('Wordlists Dir is empty skipping')
        sys.exit(1)

    # wordlists logic
    if options.w == 'ALL':
        wordlists = ''
        for wl in wordlist_full:
            wordlists += wl + ' '
    else:
        wordlists = wordlist_full[wordlist_args.index(options.w)] + ' '

    #rules logic
    rules = ''
    if options.r is not None:
        rules = '-r '
        rules += rulelist_full[rulelist_args.index(options.r)] + ' '

    # ensure the infile exists
    if os.path.isfile(options.infile):
        hash_file = options.infile
    else:
        print('Error: file {} is not a file'.format(options.infile))
        sys.exit(1)

    # hash type logic
    hash_types = ['netNTLMv1', 'netNTLMv2', 'kerberoast', 'asreproast', 'dcc2', 'NTLM']
    hash_ids = ['5500', '5600', '13100', '18200', '2100', '1000']
    hash_id = hash_ids[hash_types.index(options.m)]

    outputfile = ''
    if options.o is not None:
        outputfile = ' -o '
        outputfile += options.o

    hashcat_command = 'hashcat -a 0 -m {} {} {}{}-w4 -O{}'.format(hash_id, hash_file, wordlists, rules, outputfile)
    print(hashcat_command)
    yn = input('Are you ready? (Y/n): ')
    if yn.lower() == 'y':
        os.system(hashcat_command)

        if options.s:
            os.system('sudo shutdown')
