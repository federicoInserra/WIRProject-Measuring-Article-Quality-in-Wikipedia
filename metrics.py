import math

def calculate_Z(topK, real_rank, predict_rank):
    labels = {'FA': [], 'GA':[], 'B': [], 'C': [], 'NOL': []}
    
    for country in real_rank:
        
        label = real_rank[country]
        labels[label].append(country)

    perfect_rank = labels['FA'] + labels['GA'] + labels['B'] + labels['C'] + labels['NOL']
    
    perfect_score = 0
    for i in range(topK):
        
        country = perfect_rank[i]
        p = i + 1
        if real_rank[country] == 'FA':
            score = (pow(2,4) - 1) / math.log(1+p)
        
        elif real_rank[country] == 'GA':
            score = (pow(2,3) - 1) / math.log(1+p)
        
        elif real_rank[country] == 'B':
            score = (pow(2,2) - 1) / math.log(1+p)
        
        elif real_rank[country] == 'C':
            score = (pow(2,1) - 1) / math.log(1+p)
        
        else:
            score = 0
        
        
        perfect_score += score
    
    return perfect_score


def NDCG_score(real_rank, predict_rank , topK):

    # FA = 12, GA = 10, B = 59, C = 123, NOL = 2

    total = 0
    
    for i in range(topK):
        
        try:
            p = i + 1
            country = predict_rank[i][0]
            if real_rank[country] == 'FA':
                score = (pow(2,4) - 1) / math.log(1+p)
            
            elif real_rank[country] == 'GA':
                score = (pow(2,3) - 1) / math.log(1+p)
            
            elif real_rank[country] == 'B':
                score = (pow(2,2) - 1) / math.log(1+p)
            
            elif real_rank[country] == 'C':
                score = (pow(2,1) - 1) / math.log(1+p)
            
            else:
                score = 0
        except:
            score = 0
            pass
        
        total += score
    
    Z = calculate_Z(topK, real_rank, predict_rank)   
    print("THIS IS PERFECT SCORE",Z)
    return total/Z

