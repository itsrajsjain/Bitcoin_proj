import logic

if __name__ == "__main__":
    trusted_party = logic.TrustedThirdParty()
    system = logic.SupplyChainSystem()
    choice1=-1
    while choice1!=3:
        choice1= int(input( "Select any one of the following : \n" +"Click 0 : Add Manufacturer \n" + "Click 1 : Add Distributer \n" +"Click 2 : Add client \n"+"Click anything else : Exit\n"))
        if choice1==0:
            x=input("enter manufacturer name : ")
            manufacturer = logic.Manufacturer(x)
        elif choice1 == 1:
            x=input("enter Distributer name : ")
            y=input("enter Distributer balance : ")
            system.register_distributor(x,y,trusted_party)         
        elif choice1 == 2:
            x=input("enter Client name : ")
            y=input("enter Client balance : ")
            system.register_client(x,y,trusted_party)
        else:
            break;
    
    blockchain = logic.Blockchain();
    blockchain.register_node("Node1")
    blockchain.register_node("Node2")
    choice =-1
    while(True):
        choice= int(input("Select any one of the following : \n" +
            "Click 0 : Add transactions \n" +
            "Click 1 : See transactions added \n" +
            "Click 2 : Start mining block \n" +
            "Click 3 : confirm delivery\n" +
            "Click 4 : print blockchain\n" +
            "Click 5 : QR code status\n" +
            "Click 6 : distributer confirms dispatch\n" +
            "Click 7 : issue with delivery(only if you have not received the product)\n" +
            "Click 8 : distributer initiates delivery\n"
            "Click 9 : Show balance\n"
            "Click 10 : Exit\n"))
        if choice==0:
            client_name = input("client name: \n")
            distributer_name = input("Distributer name: \n")
            product_name= input("product name: \n")
            product_id= int(input("product id: \n"))
            amount= int(input("amount: \n"))
            blockchain.new_transaction(logic.Transaction(product_id,product_name,distributer_name,client_name,amount))
        elif choice==1:
            print("Transactions: \n")
            for mm in blockchain.current_transactions:
                print("client name: ", mm.client)
                print("Distributer name: ", mm.distributor)
                print("product id", mm.product_id)
                print("product name", mm.product_name)
                print("amount", mm.amount)
        elif choice==2:
            mined_block = blockchain.mine_block()
        elif choice==3:
            distributer_name=input("enter distributer name \n")
            product_id=int (input("enter product id \n"))
            f1=0
            for transaction in blockchain.current_transactions:
                if transaction.distributor ==distributer_name and transaction.product_id==product_id:
                    f1=1
                    transaction.client_confirm()   
            if  f1==0:
                print("No such transaction exists")
        elif choice==4:
            print("Blockchain:")
            for block in blockchain.chain:
                print("\nBlock:", block['index'])
                print("Timestamp:", block['timestamp'])
                print("Previous Hash:", block['previous_hash'])
                print("Proof:", block['proof'])
                print("Merkle Root:", block['merkle_root'])
                print("Transactions:", block['transactions'])
        elif choice==5:
            distributer_name=input("enter distributer name \n")
            product_id=int(input("enter product id \n"))
            flag=0
            for nn in blockchain.current_transactions:
                if nn.distributor ==distributer_name and nn.product_id==product_id:
                    flag=1
                    qr=logic.QR()
                    qr.new_transaction(nn)
                    qr.generate_qr_code()
            if flag==0:
                print("No such transaction exists")
        elif choice==6:
            distributor_name=input("enter distributer name \n")
            distributor=system.get_distributor(distributor_name)
            distributor.confirm_dispatch()  
        elif choice==7:
            distributer_name=input("enter distributer name \n")
            client_name = input("client name: \n")
            product_id=int (input("enter product id \n"))
            ff=0
            for transaction in blockchain.current_transactions:
                if transaction.distributor ==distributer_name and transaction.product_id==product_id:
                    ff=1
                    if (transaction.distributor_confirmed==True) and (transaction.client_confirmed==False):
                        print("Distributor claims to have sent the product, but the client denies receiving it.")
                        print("client name: ", transaction.client)
                        print("Distributer name: ", transaction.distributor)
                        print("product id", transaction.product_id)
                        print("product name", transaction.product_name)
                        print("amount", transaction.amount)
                        print("as the Transaction in the blockchain suggests that product was indeed dispached therefore client will get 100 rupees deducted")
                        transaction.client_confirm=True
                        trusted_party.deduction(client_name,100)
                    elif (transaction.distributor_confirmed==False) and (transaction.client_confirmed==False):
                        print("Client claims not to have received the product, but the distributor claims to have sent the product")
                        print("client name: ", transaction.client)
                        print("Distributer name: ", transaction.distributor)
                        print("product id", transaction.product_id)
                        print("product name", transaction.product_name)
                        print("amount", transaction.amount)
                        print("as the Transaction in the blockchain suggests that product was indeed NOT dispached therefore distributer will get 200 rupees deducted")
                        trusted_party.deduction(distributer_name,200)          
            if ff==0:
                print("No such transaction exists") 
        elif choice==8:
            distributer_name=input("enter distributer name \n")
            product=input("enter product name \n")
            distributer=system.get_distributor(distributer_name)
            client_name = input("client name: \n")
            distributer.deliver(product,client_name,blockchain)
        elif choice==9:
            name=input("enter name \n")
            balance = trusted_party.get_deposit(name);
            print(f"name: {name}, your balance is : {balance}")
        elif choice==10:
            break
    




