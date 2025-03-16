import random
computer=random.randint(a=1,b=10)
guess=int(input("guess the number: "))
if guess==computer:
    print("win")
else:
    print(f"you lose\nthe number is : {computer}" )    
