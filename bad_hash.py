import rpc
import transaction

s = rpc.jsonrpc("bitcoinrpc", "Ck9SwPoZ76gaiLex88r7aKspUrFUFEDffai9mzRjDi7W")
hash = '6632b2656832f20a411b53ac6f7923404193308b6c09e3dd4e5a0f9fac4c33d6'
t = transaction.transaction(hash,s)
print(t.verify())
