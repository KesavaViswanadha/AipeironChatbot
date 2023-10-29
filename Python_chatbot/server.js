import { createClient } from "@supabase/supabase-js";
import OpenAIApi from "openai";
import { spawn } from 'child_process';
import { promises as fs } from 'fs';
import { createInterface } from 'readline';

/**const supabaseClient = createClient("https://vswuyfouifxhjyloqbdl.supabase.co", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZzd3V5Zm91aWZ4aGp5bG9xYmRsIiwicm9sZSI6ImFub24iLCJpYXQiOjE2OTg1Mzk3NDQsImV4cCI6MjAxNDExNTc0NH0.LoSboreByG0r1ly6ePCk3Ve2Ewf-v_ko4iXRoxojiz8");
const openai = new OpenAIApi({
    apiKey: "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"
  });*/
//const { spawn } = require('child_process');
//const fs = require('fs').promises; // Use the promise-based version of the 'fs' module

async function callDocChunker(filePath) {
  return new Promise((resolve, reject) => {
    const pythonProcess = spawn('python3', ['document_chunker.py', filePath]);

    pythonProcess.on('close', async (code) => {
      if (code === 0) {
        try {
          // Read the results from the file written by the Python script
          const dataString = await fs.readFile('output.json', { encoding: 'utf8' });
          const result = JSON.parse(dataString);
          resolve(result);
        } catch (e) {
          reject(e);
        }
      } else {
        reject(`child process exited with code ${code}`);
      }
    });
  });
}

async function callQueryBot(this_question) {
  return new Promise((resolve, reject) => {
    const pythonProcess = spawn('python3', ['query_bot.py', this_question]);

    pythonProcess.on('close', async (code) => {
      if (code === 0) {
        try {
          // Read the results from the file written by the Python script
          const dataString = await fs.readFile('output_query.json', { encoding: 'utf8' });
          const result = JSON.parse(dataString);
          resolve(result);
        } catch (e) {
          reject(e);
        }
      } else {
        reject(`child process exited with code ${code}`);
      }
    });
  });
}

async function callQueryBotVectara(this_question) {
  return new Promise((resolve, reject) => {
    const pythonProcess = spawn('python3', ['vectara_chatbot.py', this_question]);

    pythonProcess.on('close', async (code) => {
      if (code === 0) {
        try {
          // Read the results from the file written by the Python script
          const dataString = await fs.readFile('output_query_vectara.json', { encoding: 'utf8' });
          const result = JSON.parse(dataString);
          resolve(result);
        } catch (e) {
          reject(e);
        }
      } else {
        reject(`child process exited with code ${code}`);
      }
    });
  });
}

// function embedText(inputText) {
//     try {
//         var result = ""
//         return new Promise ((resolve) => {
//             openai
//                 .createEmbedding ({
//                     model: "text-embedding-ada-002",
//                     input: inputText,
//                 })
//                 .then ((res) => {
//                     //console. log (res.data ['data'] [0] ["embedding"])
//                     result = res.data["data"][0]["embedding"];
//                 });
//             setTimeout (() => {
//                 resolve (result);
//             }, 2000);
//         });
//     } catch (error) {
//         console.error(err);
//     }
// }

const readline = createInterface({
  input: process.stdin,
  output: process.stdout
});

async function generateEmbeddings() {
    //const configuration = new Configuration({ apiKey: "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"});

    const documents = await callDocChunker("/Users/kesvis/skylerProject/calhacks10/Python_chatbot/i941taxdoc.pdf");

    try {
      const userResponse = new Promise((resolve) => {
          readline.question('Please enter a prompt? ', (answer) => {
              resolve(answer);
          });
      });

      // Wait for the user to respond
      const this_prompt = await userResponse;

      // Call the bot with the user's input and wait for the response
      const answer_to_prompt = await callQueryBot(this_prompt);
      const answer_to_prompt_vectara = await callQueryBotVectara(this_prompt);
      // Log the answer and close the readline interface
      console.log(answer_to_prompt_vectara);
      //console.log(answer_to_prompt);
      readline.close();

  } catch (error) {
      // Handle any errors that may occur during the document chunking or vectara call
      console.error('An error occurred in generateEmbeddings:', error);
      readline.close();
  }
 
    
    
    /**console.log(answer_to_prompt);
    
    const answer_to_prompt_vectara = await callQueryBotVectara("How do I fill out form 941 properly if I am a large business in a hurricane?");
    console.log(answer_to_prompt_vectara);*/
 
  }
  

generateEmbeddings();
   // for (const document of documents) {
    //     const input = document.replace(/\n/g, '');
    //     embedText(input).then(async (result) => {

    //         const { data, error } = await supabaseClient
    //             .from("documents")
    //             .insert({
    //                 content: document,
    //                 embedding: result
    //             });
    //         setTimeout(() => {}, 500);
    //     });
        /**const embeddingResponse = await openai.createEmbedding({
            model: "text-embedding-ada-002",
            input
        })

        const [{ embedding }] = embeddingResponse.data.data;

        await supabaseClient.from('document').insert({
            content: document,
            embedding
        })*/