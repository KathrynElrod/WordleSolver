class WordleSolver:
  def __init__(self, verbose=False):
    # Number of guesses in a game
    self.MAX_NUM_GUESSES = 6
    
    # List of 5-letter words, sorted by commonality
    with open('words.txt') as file:
      self.WORDS = [line.strip() for line in file.readlines()]
    
    # Initial guess
    self.guess = 'tears'
    
    # Knowledge base
    self.green_letters = [None, None, None, None, None]
    self.yellow_letters = [[], [], [], [], []]
    self.grey_letters = []
    
    # State variables
    self.empties = 0
    self.prev_empties = 5
    self.guess_num = 1
    self.have_searched_uniques = False
    self.squares = ''
    self.verbose = verbose
  
  def start(self):
    print('[ 🟩:g  🟨:y  ⬜:↵  🚫:x ]')
    if self.verbose:
      print('[*] Starting with pre-defined word "'+self.guess+'"')
    while self.guess_num <= self.MAX_NUM_GUESSES:
      # Give guess
      print('Guess '+str(self.guess_num)+': '+self.guess.upper())
      
      # Prompt
      self.prev_empties = self.empties
      self.empties = 0
      found_invalid = False
      for index, letter in enumerate(self.guess):
        # Fill in known letters
        if self.green_letters[index]==letter:
          print(letter.upper()+': ▒')
          self.squares += '▒▒'
          continue
        elif letter in self.yellow_letters[index]:
          print(letter.upper()+': ░')
          self.squares += '░░'
          continue
        
        # Ask about unknown letters
        color = input(letter.upper()+'? ')
        if color=='x':
          # Not a valid word
          found_invalid = True
          break
        elif color=='g':
          self.green_letters[index] = letter
          self.squares += '▒▒'
        elif color=='y':
          self.yellow_letters[index].append(letter)
          self.squares += '░░'
        else:
          self.grey_letters.append(letter)
          self.squares += '  '
          self.empties += 1
      self.squares += '\n'
      
      if found_invalid:
        print('"'+self.guess+'" marked as invalid word')
        self.WORDS.remove(self.guess)
        self.guess = self.make_guess()
        continue
      
      # Did we finish?
      if all(self.green_letters):
        print('\nWordle solved!')
        print('Word is: '+''.join(self.green_letters).upper())
        self.print_graphic()
        break
      if self.guess_num>=self.MAX_NUM_GUESSES:
        print('Wordle failed :(')
        self.print_graphic()
        break
      else:
        print()
      
      if self.verbose:
        possible_guesses = self.make_next_guess(True)
        len_pg = len(possible_guesses)
        print('[*] '+str(len_pg)+' possible word'+('s' if len_pg!=1 else '')+' from this point')
        if len_pg>1:
          print('[*] '+('First 10: ' if len_pg>10 else '')+str(possible_guesses[:10]))
      
      self.guess = self.make_guess()
      self.guess_num += 1
  
  def print_graphic(self):
    print('┌────────────┐')
    for line in self.squares.splitlines():
      print('│ '+line+' │')
    print('└────────────┘')
  
  # Decide what word to guess next
  def make_guess(self):
    if self.guess_num<(self.MAX_NUM_GUESSES-1) and self.empties==self.prev_empties and not self.have_searched_uniques:
      possible_guesses = self.make_next_guess(True)
      if len(possible_guesses) > (self.MAX_NUM_GUESSES-self.guess_num):
        # There are more possibilities than guesses remaining
        if self.verbose:
          print('[*] Only '+str(self.MAX_NUM_GUESSES-self.guess_num)+' guesses remaining')
        
        eg = self.make_expoloratory_guess(possible_guesses)
        if eg:
          return eg
    return self.make_next_guess()

  # Find a word that gives us the most new and useful information
  def make_expoloratory_guess(self, possible_guesses):
    # Get every previously guessed letter
    found_letters = [letter for letter in self.green_letters if letter]
    found_letters += self.grey_letters
    for list in self.yellow_letters:
      found_letters += list
    
    # Get every not-yet-guessed letter in remaining possibilities
    find_letters = ''
    for pg in possible_guesses:
      for letter in pg:
        if not (letter in found_letters or letter in find_letters):
          find_letters += letter
    
    if self.verbose:
      print('[*] Finding the word that contains the most letters from ['+find_letters+']')
    
    # Find the word that contains the most letters from find_letters
    best_word = ('', 0)
    for word in self.WORDS:
      count = 0
      duplicate = False
      for letter in word:
        if word.count(letter)>1:
          duplicate = True
        if letter in find_letters:
          count += 1
      if duplicate:
        continue
      if count > best_word[1]:
        best_word = (word, count)
    
    # If we found one, return it
    if best_word[1]>2:
      if self.verbose:
        print('[*] Found: "'+best_word[0]+'" with '+str(best_word[1])+' letters')
      self.have_searched_uniques = True
      return best_word[0]
    
    if self.verbose:
      print('[*] Not found. Guessing next most common possible word.')
    return None
  
  # Look through words and select first which fits the kbase
  def make_next_guess(self, all=False):
    guesses = []
    for word in self.WORDS:
      if self.is_valid_word(word):
        if all:
          guesses.append(word)
        else:
          return word
    if all:
      return guesses
    else:
      print('No word found :(')
      self.print_graphic()
      exit()
  
  # Determine if a given word fits the kbase
  def is_valid_word(self, word):
    word_minus_greens = word
    for index, letter in enumerate(self.green_letters):
      if letter and not word[index]==letter:
        return False
      elif letter:
        word_minus_greens = word_minus_greens[:index]+'-'+word_minus_greens[index+1:]
    
    for index, letter_list in enumerate(self.yellow_letters):
      for letter in letter_list:
        if word[index]==letter or not letter in word:
          return False
    
    for letter in self.grey_letters:
      if letter in word_minus_greens:
        return False
    
    return True

if __name__=='__main__':
  choice = input('Run verbose? ')
  verbose = choice and choice.lower()[0]=='y'
  print('▔▔▔▔▔▔▔▔▔▔▔▔' + ((1+len(choice))*'▔' if choice else '') )
  solver = WordleSolver(verbose)
  solver.start()

