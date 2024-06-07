'''
Created on 14-Apr-2024

@author: pakala
'''
try:
    from utils.sip import Actor,AState
except ImportError:
    from src.main.utils.sip import Actor,AState

try:
    from utils.utils import ProductionStepOrder
except ImportError:
        from src.main.utils.utils import ProductionStepOrder
    
class WaitforNewOrder(AState):
    message_in =  ["ProductionOrderCyclic"]       
    
    def initialize(self):
        # Gaurd variables for enabling the transitions
        self.createProductionStepSeq_Enabled = True          
    
    def actions(self) -> None:
        if (self.wait_untill_message(1, WaitforNewOrder.message_in)):
            message = self.receive(WaitforNewOrder.message_in[0])
            self.save_in_message(message)
            self.push("ProductionOrder", message)
        else:
            self.actions()
        
    def transitions(self) -> object:
        if (self.createProductionStepSeq_Enabled):
            return "CreateProductionStepSeq"
      
class CreateProductionStepSeq(AState):
    
    def initialize(self):
        # Gaurd variables for enabling the transitions
        self.sendProductionStepOrder_Enabled = True
        self.WaitforNewOrder_Enabled = True
    
    def actions(self) -> None:
        message = self.retrieve("ProductionOrder")
        data, status2 = self.base_class.shellObject.add_produtionCapability(message["interactionElements"][0])
        if status2:
            self.WaitforNewOrder_Enabled = False
        else:
            self.excProductionStepSeq_Enabled = False
        
    def transitions(self) -> object:
        if (self.sendProductionStepOrder_Enabled):
            return "SendProductionStepOrder"

        if (self.WaitforNewOrder_Enabled):
            return "WaitforNewOrder"        

class SendProductionStepOrder(AState):
    
    def initialize(self):
        # Gaurd variables for enabling the transitions
        self.WaitforNewOrder_Enabled = True
            
    
    def actions(self) -> None:
        aasIdentifier1 = self.retrieve("ProductionOrder")["frame"]["receiver"]["id"]
        
        try:
            pso = ProductionStepOrder(self.base_class.pyaas,aasIdentifier1)
            conversationID,status = pso.createProductionStepOrder(aasIdentifier1)
            if status:
                pass
            else:
                pass
        except  Exception as e:
            print(str(e))
        
        self.flush_tape()
        
    def transitions(self) -> object:
        
        if (self.WaitforNewOrder_Enabled):
            return "WaitforNewOrder"

class PMCyclic(Actor):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''      
        Actor.__init__(self,"PMCyclic",
                       "www.admin-shell.io/interaction/productionmanagementcyclic",
                       "PMCyclic","WaitforNewOrder")
                        

    def start(self):
        self.run("WaitforNewOrder")


if __name__ == '__main__':
    
    lm2 = PMCyclic()
    lm2.Start('msgHandler')
