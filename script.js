const wordsContainer = document.getElementById('words-container');


const API_URL = 'http://localhost:8000';


const VOWELS = "аеёиоуыэюя";
let words = []; 
let correctIndex = -1;
let word_limit = 30

async function fetchWords() {  // ПОЛУЧЕНИЕ СЛОВ С БЭКЕНДА
    try {
        const response = await fetch(`${API_URL}/words/random?limit=${word_limit}`);
        const data = await response.json();
     
        words = data
        displayCurrentWord()
        return words
        
    } catch (error) {
        console.error("Ошибка при загрузке слов:", error);
        wordsContainer.textContent = `Не удалось загрузить слова${error}`;
    }
}

function displayCurrentWord() {
    if (words.length === 0){
         wordsContainer.innerHTML = `
            <div style="text-align: center;">
                <h2>Уверен что точно все запомнил?</h2>
                <button onclick="location.reload()" style="padding: 10px 20px;font-family: 'Courier New', Courier, monospace; font-size: 18px; cursor: pointer; border-radius: 8px; border: none; background-color: #4CAF50; color: white; margin-top: 20px;">Хочу еще</button>
            </div>
        `;
        return; 
    }; 
    wordsContainer.innerHTML = '';
    const randomIndex = Math.floor(Math.random() * words.length);
    const wordObject = words.splice(randomIndex, 1)[0];
    correctIndex = wordObject.accent_index;
    const poppedWord = wordObject.word.toLowerCase();
    const wordDiv = document.createElement('div');
    wordDiv.classList.add('word')
    for (let i =0; i < poppedWord.length;i++){
        let type = ''
        const letter = document.createElement('span')
        letter.textContent = poppedWord[i]
        const isVowel = VOWELS.includes(poppedWord[i].toLowerCase());
        letter.classList.add(isVowel ? 'vowel' : 'consonant');
        letter.dataset.index = i;
        wordDiv.appendChild(letter)
        
    }
    
    wordsContainer.appendChild(wordDiv)



   
    
    
}

fetchWords();


wordsContainer.addEventListener('click',(e)=>{
    const clickedLetter = e.target.closest('span');
    if (!clickedLetter) return;
    
  
    if (clickedLetter.classList.contains("vowel") && correctIndex !== -1) {
        const index = parseInt(clickedLetter.dataset.index);
        if (index === correctIndex){
            clickedLetter.classList.add('correct_letter')//добавить зелены цвет
            setTimeout(displayCurrentWord, 600); 

        }else{
            clickedLetter.classList.add('incorrect_letter') // добавить красны цвет
        }
       

    }

})
    