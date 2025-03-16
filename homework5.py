


while True:
    print('1.gam + ')
    print('2.tafrig - ')
    print('3.tagsim / ')
    print('4.zarb * ')
    print('5.tavan do ** ')
    print('6.Exit ')
    key=int(input("write a key: "))
    if key==6:
        print('exit')
        break
    elif key== 1 or 2 or 3 or 4 :
        num1=int(input('write first number: '))
        num2=int(input('write second number: '))
        if key==1:
            print(f"your number is {num1 +num2}")
        elif key==2:
            print(f"your number is {num1 - num2}")
        elif key==3:
            print(f"your number is {num1 //num2}")     
        elif key==4:
            print(f"your number is {num1 *num2}")        
    elif key==5:
        num3=int(input('write a number: '))  
        print(f"your number is {num3**2}") 
    else:
        print('deta is not the match')         
