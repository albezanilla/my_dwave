import sys
import pickle
from dwave.system.samplers import DWaveSampler
from dwave.system.composites import FixedEmbeddingComposite

usage_message = 'Usage: run_dwave.py label'

if len(sys.argv) == 2:
    run_label = sys.argv[1]
else:
    print(usage_message)
    sys.exit(1)


bqm_filename = 'bqm.pickle'
embedding_filename = 'embedding.pickle'
result_filename = 'run_dwave.' + run_label + '.pickle'

sampler = DWaveSampler(solver='DW_2000Q_LANL')

try:
    with open(bqm_filename, 'rb') as f:
        bqm = pickle.load(f)
except FileNotFoundError:
    print('error: file "%s" does not exist' % filename)
    sys.exit(1)

try:
    with open(embedding_filename, 'rb') as f:
        embedding = pickle.load(f)
except FileNotFoundError:
    print('error: file "%s" does not exist' % filename)
    sys.exit(1)

sampler = FixedEmbeddingComposite(sampler, embedding)
response = sampler.sample(bqm, num_reads=1000, chain_strength=2.0)

print(response.first)

f = response.record['sample']
print(f[0])
print(f[1])
print(f[2])

try:
    with open(result_filename, 'wb') as f:
        pickle.dump(response, f, pickle.HIGHEST_PROTOCOL)
except FileNotFoundError:
    print('error: file "%s" does not exist' % filename)
    sys.exit(1)
