import tempfile
import os
import argparse

# Running LDPred

""" 
    --tf relative path to training file
    --vf relative path to validation/testing file
    --N number of individuals
    --p comma separated values of p to test with (default 1.0,0.3,0.1,0.03,0.01,
        0.003,0.001,0.0003,0.0001)
    --R LD pred radius
    --o text output filepath
"""

parser = argparse.ArgumentParser()
parser.add_argument("--tf", help="relative path to training file (.bed, .bim, and .fam files needed in same location, omit file-extention)")
parser.add_argument("--vf", help="relative path to validation/testing file (.bed, .bim, and .fam files needed in same location, omit file-extention)")
parser.add_argument("--N", help="number of individuals")
parser.add_argument("--p", help="comma separated values of p to test with (default 1.0,0.3,0.1,0.03,0.01,0.003,0.001,0.0003,0.0001)")
parser.add_argument("--R", help="LD pred radius")
parser.add_argument("--o", help="output directory")
args = parser.parse_args()
all_args = ["tf", "vf", "N", "p", "R", "o"]
args_dict = vars(args)
if (set(filter(lambda x: args_dict[x] != None, vars(args))) != set(all_args)):
    raise Exception('You did not specify all arguments')


"""First generate the summary statistics file"""
os.system("./plink/plink --noweb --bfile {} --assoc --out {}/sum_stats_raw".format(args_dict['tf'], args_dict['o'])) # generate the plink file

from helpers import assoc_to_ssf

print("creating a formatted summary statistics file...")
assoc_to_ssf.assoc_to_ssf('{}/sum_stats_raw.assoc'.format(args_dict['o']), args_dict['o'])


print("Running LD Pred...")

coord_string = '{}/coordination_file'.format(args_dict['o'])
coord_file = '{}.coord.hdf5'.format(coord_string)

os.system('rm {}/coordination_file.coord.hdf5'.format(args_dict['o']))
print('Coordinating test data into file %s' % coord_file)

cmd_str = 'python ./ldpred/coord_genotypes.py --gf={}\
           --vgf={} --ssf={}/sum_stat_fmt.txt --N={}\
           --out={}'.format(args_dict['tf'], args_dict['vf'], 
                            args_dict['o'], args_dict['N'], 
                            coord_file, args_dict['o'])
print(cmd_str + '\n')
assert os.system(cmd_str) == 0, 'Error (when coordinating data)! Stopping...'

out_file = '{}.res'.format(coord_string)
print('Coordinating test data with LD file and results file prefix: %s ' % out_file)

cmd_str = 'python ./ldpred/LDpred.py --coord={}\
           --ld_radius={}  --local_ld_file_prefix={}\
           --PS={} --N={}  --out={}'.format(coord_file, args_dict['R'], 
                                            out_file, args_dict['p'],
                                            args_dict['N'], out_file, args_dict['o'])
assert os.system(cmd_str) == 0, 'Problems when running LDpred!  Testing stopped'

print('Validating results with output file prefix: %s' % out_file)

cmd_str = 'python ./ldpred/validate.py --vgf={} --rf={}  --out={}'.format(args_dict['vf'],
            outfile, outfile, args_dict['o'])
assert os.system(cmd_str) == 0, 'Problems with the validation step!  Testing stopped'
print('Test finished successfully!')
