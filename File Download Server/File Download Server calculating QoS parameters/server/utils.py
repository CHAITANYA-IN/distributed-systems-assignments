def length(iterable):
    count = 0
    for _ in iterable:
        count += 1
    return count


def split(str1: str, str2: str):
    len1 = length(str1)
    len2 = length(str2)
    ptr1 = 0
    found = [-len2, ]
    strings = []
    while(ptr1 < len1):
        if(str1[ptr1] == str2[0]):
            if(str1[ptr1:ptr1+len2] == str2):
                found.append(ptr1)
                ptr1 += len2
            else:
                ptr1 += 1
        else:
            ptr1 += 1
    index = 1
    lenFound = length(found)
    while(index < lenFound):
        strings += [str1[found[index-1]+len2:found[index]]]
        index += 1
    strings += [str1[found[index-1]+len2:]]
    return strings
