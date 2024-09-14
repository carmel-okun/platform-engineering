import dns.resolver
answer = dns.resolver.resolve('www.google.com', 'CNAME')
rdt = dns.rdatatype.to_text(answer.rdtype)
print(rdt)
