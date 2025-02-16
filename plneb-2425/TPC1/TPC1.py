#Create a function that:

#1. given a string "s", reverse it.

teste = "Uma frase aleatória para testar"
def reverse_string(s):
    return s[::-1]

print(reverse_string(teste))

#2. given a string "s", returns how many "a" and "A" characters are present in it.

def character_amount(s):
    return s.upper().count("A")

print(character_amount(teste))

#3. given a string "s", returns the number of vowels there are present in it.

def count_vowels(s):
    vowels = "aeiouAEIOUáÁéÉíÍóÓúÚâÂêÊîÎôÔûÛãÃõÕ"
    return sum(1 for char in s if char in vowels)

# Example usage

print(count_vowels(teste))

#4. given a string "s", convert it into lowercase.

def lowercase(s):
    return s.lower()

print(lowercase(teste))

#5. given a string "s", convert it into uppercase.

def uppercase(s):
    return s.upper()

print(uppercase(teste))

#6. Verifica se uma string é capicua

testepalindromo = "level"

def palindromo(s):
    return s == s[::-1]

print(palindromo(testepalindromo))

#7. Verifica se duas strings estão balanceadas (Duas strings, s1 e s2, estão balanceadas se todos os caracteres de s1 estão presentes em s2.)

def balanceadas(s1, s2):
    return all(char in s2 for char in s1)

print(balanceadas("awe", "aeiou"))

#8. Calcula o número de ocorrências de s1 em s2

def ocorrencias(s1, s2):
    return s2.count(s1)

print(ocorrencias("ab", "ababasb"))

#9. Verifica se s1 é anagrama de s2.

def anagramas(s1, s2):
    return sorted(s1) == sorted(s2)

#"listen" e "silent": Deve imprimir True
s1 = "listen"
s2 = "silent"
print(anagramas(s1, s2))

#"hello", "world": Deve imprimir False
s1 = "hello"
s2 = "world"
print(anagramas(s1, s2))

#10. Dado um dicionário, calcular a tabela das classes de anagramas.

def dicionario_anagramas(dicionario):
    anagramas = {}

    for palavra in dicionario:

        chave = ''.join(sorted(palavra))
        
        if chave not in anagramas:
            anagramas[chave] = []
        
        anagramas[chave].append(palavra)

    return list(anagramas.values())

dicionario = ["abra", "bara", "raba", "teste", "etset", "amor", "roma", "ramo"]
tabela = dicionario_anagramas(dicionario)

for grupo in tabela:
    print(grupo)