import hashlib
  
snippet = "test"

snippetHash = hashlib.sha256()
serializedSnippet = str(snippet).encode("UTF-8")
snippetHash.update(serializedSnippet)

result = snippetHash.hexdigest()

print(result)