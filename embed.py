import pickle
import minorminer
from dwave.system.samplers.dwave_sampler import DWaveSampler

in_filename = 'bqm.pickle'

try:
    with open(in_filename, 'rb') as f:
        bqm = pickle.load(f)
except FileNotFoundError:
    print('error: file "%s" does not exist' % filename)
    sys.exit(1)

sampler = DWaveSampler(solver='DW_2000Q_LANL')

hdw_adj = []

for node in sampler.adjacency:
    for neighbor_node in sampler.adjacency[node]:
        hdw_adj.append((node,neighbor_node))
    
best_total_qubits = 1000
best_longest_chain = 20

for i in range(100):
    embedding = minorminer.find_embedding(bqm.quadratic, hdw_adj)

    emb_filename = 'embedding.' + str(i) + '.pickle'
    with open(emb_filename, 'wb') as f:
        pickle.dump(embedding, f, pickle.HIGHEST_PROTOCOL)

    total_qubits = 0
    longest_chain = 0
    for var in embedding:
        total_qubits += len(embedding[var])
        if len(embedding[var]) > longest_chain:
            longest_chain = len(embedding[var])

    print('**************** i=%d ****************' % i)
    print('total qubits used = %d' % total_qubits)
    print('longest chain = %d' % longest_chain)

    if total_qubits < best_total_qubits and longest_chain < best_longest_chain:
        best_embedding = embedding
        best_total_qubits = total_qubits
        best_longest_chain = longest_chain

print('best total qubits used = %d' % best_total_qubits)
print('best longest chain = %d' % best_longest_chain)
