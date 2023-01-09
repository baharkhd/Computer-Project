from anytree import Node, RenderTree
import json
import re
from statics import *

#udo = Node("Udo")
#marc = Node("Marc", parent=udo)
#lian = Node("Lian", parent=marc)
#dan = Node("Dan", parent=udo)
#jet = Node("Jet", parent=dan)
#jan = Node("Jan", parent=dan)
#joe = Node("Joe", parent=dan)

# Todo: transfer this function to Writer class
def write_parse_tree(root_node, PATH='parse_tree.txt'):

    tree_lines = ''
    with open(PATH, "+w", encoding="utf-8") as file:
        for pre, fill, node in RenderTree(root_node):
            tree_lines += "%s%s" % (pre, node.name)
            if node.name != "$":
                tree_lines += '\n'

        file.write(tree_lines)
    

class Parser:
    def __init__(self, json_data):
        self.parse_table = json_data['parse_table']
        self.grammar = json_data['grammar']
        self.first = json_data['first']
        self.follow = json_data['follow']
        self.terminals = json_data['terminals']
        self.non_terminals = json_data['non_terminals']
        self.token_pointer = 0
        self.stack = ['0']
        self.node_stack = []
        self.root_node = None

        self.current_node = None


    def return_action(self, action):
        action_type = ActionType.REDUCE
        state = '0'

        if re.match(r'reduce_[0-9]+', action):
            action_type = ActionType.REDUCE
            state = action.split('_')[1]
        elif re.match(r'shift_[0-9]+', action):
            action_type = ActionType.SHIFT
            state = action.split('_')[1]

        return action_type, state


    def is_terminal(self, token):
        if token in self.terminals:
            return True
        return False

    def is_non_terminal(self, token):
        if token in self.non_terminals:
            return True
        return False



    def create_parse_tree(self, all_tokens):
        # tokens: (#: line_num, TOKEN_TYPE, token)
        while True:

            #if self.token_pointer == len(all_tokens):

            print("****", self.stack)
            #print("@@@@@", self.node_stack)
            token_tuple = all_tokens[self.token_pointer]
            token_type = token_tuple[1]
            token = token_tuple[2]
            

            if token_type == TokenType.KEYWORD_ID.value and token in tokens[TokenType.KEYWORD]:
                token_type = TokenType.KEYWORD.value
            elif token_type == TokenType.KEYWORD_ID.value:
                token = TokenType.ID.value
                token_type = TokenType.ID.value
            elif token_type == TokenType.NUM.value:
                token = TokenType.NUM.value
                token_type = TokenType.NUM.value

            latest_state = self.stack[-1]
                
            print(token_tuple, token_type, token)
            action = self.parse_table[latest_state][token]
            
            if action == 'accept':
                print("!!!!!!!!accepted\n\n")
                self.stack.pop()
                root_node = self.stack.pop()

                self.root_node = self.node_stack[0]
                self.node_stack[2].parent = self.root_node

                #print(self.root_node, self.node_stack[2])

                for pre, fill, node in RenderTree(self.root_node):
                    #print("+++", node)
                    print("%s%s" % (pre, node.name))
                write_parse_tree(self.root_node)
                break

            action_type, next_state = self.return_action(action)
            
            if action_type == ActionType.SHIFT:
                self.stack += [token, next_state]
                if token_tuple[2] != '$':
                    self.node_stack += [Node('({}, {})'.format(token_type, token_tuple[2])), '']
                else:
                    self.node_stack += [Node('$'), '']
                if not token == '$':
                    self.token_pointer += 1

            else:
                grammar_id = self.parse_table[latest_state][token].split('_')[1] # since it is goto_#
                next_gram = self.grammar[grammar_id]
                parent_token = next_gram[0]
                parent_node = Node(parent_token)
                popped_tokens = []

                is_epsilon = next_gram[2] == 'epsilon'

                if not is_epsilon:
                    right_tokens_num = len(next_gram) - 2
                else:
                    right_tokens_num = 0
                    epsilon_node = Node('epsilon', parent=parent_node)

                    print("Children:", right_tokens_num)
                    print('epsilon')

                print("Parent:", parent_token)
                print("Children:", right_tokens_num)

                
                popped_nodes = []
                for i in range(2 * right_tokens_num):
                    popped = self.stack.pop()
                    popped_node = self.node_stack.pop()
                    if i % 2 != 0:
                        print(popped)
                        popped_nodes.append(popped_node)
                print()

                popped_nodes.reverse()
                for pn in popped_nodes:
                    pn.parent = parent_node

                latest_state = self.stack[-1]
                print("++++", latest_state, parent_token)
                next_goto = self.parse_table[latest_state][parent_token].split("_")[1]
                self.stack += [parent_token, next_goto]
                self.node_stack += [parent_node, '']

                

def read_json(path='table.json'):
    f = open('table.json')
    data = json.load(f)
    f.close()

    return data


if __name__ == "__main__":



    test_json_data = make_test_json_data()
    json_data = read_json('table.json')
    parser = Parser(test_json_data)
    

    tokens = ['int', '*', 'int', '$']
    parser.create_parse_tree(tokens)

    #for k, v in parser.grammar.items():
    #    print(k, ":", v)

    #print()
    
    #for k, v in parser.parse_table.items():
    #    print(k, ":", v)


