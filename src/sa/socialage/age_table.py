from .models import AgeTable

MAX_AGE = 80

def get_table():
    table, created = AgeTable.objects.get_or_create(id=1)
    return table

# Update frequency of social age vs biological age
def age_table_add(bio, soc):
    table = get_table()
    matrix = table.table.split(',')
    matrix[bio * MAX_AGE + soc] = str(int(matrix[bio* MAX_AGE + soc]) + 1)
    table.table = ','.join(matrix)
    table.save()

# Update frequency of social age vs biological age
def age_table_sub(bio, soc):
    table = get_table()
    matrix = table.table.split(',')
    matrix[bio * MAX_AGE + soc] = str(int(matrix[bio* MAX_AGE + soc]) - 1)
    table.table = ','.join(matrix)
    table.save()

# Get distribution of social ages for a given input biological age
def age_table_bio_dist(age):
    if age < 0 or age >= MAX_AGE:
        return []
    table = get_table()
    matrix = table.table.split(',')
    soc_age_list = map(int, matrix[age*MAX_AGE:(age+1)*MAX_AGE-1])
    return list(map(lambda x,y: [str(x),y], range(0, MAX_AGE - 1), soc_age_list))

# Get distribution of biological ages for a given input social age
def age_table_soc_dist(age):
    if age < 0 or age >= MAX_AGE:
        return []
    table = get_table()
    matrix = table.table.split(',')
    bio_age_list = map(int, matrix[age::MAX_AGE])
    return list(map(lambda x,y: [str(x),y], range(0, MAX_AGE - 1), bio_age_list))