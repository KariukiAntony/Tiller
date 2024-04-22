<h1 align="center">🔥️ Tiller 🔥️</h1>
<h3 align="center"> 🚀️ Empower yourself with a personal assistant designed to seamlessly capture speech, transcribe it into text format, and provide concise summaries. Additionally, it offers the convenience of converting these summaries into speech, enabling you to listen to your notes effortlessly.</h3>

## Inspiration

Whenever am in class, i easily get distracted which makes it difficult to take notes and to concentrate in class. Reflecting on this challenge, I identified several common distractions:

- The constant pull of brainstorming new project ideas.
- Maybe i have a bug that has taken me more than a day to fix with no success.
- Difficulty hearing the lecturer's voice clearly.

This is where the idea of building tiller was born. This is a problem that i would solve using the knowledge that i had already acquired which would also make me put my skills into action.

## What it does.

Tiller captures speech using google speech recognition api, transcribes it to a text format. Once the recording is over, the recoded text is sent to the openai api to be summarized while keeping the important info intact. Once the response is recieved from openai, it is converted into speech using the tiktok text to speech and the audio is uploaded to cloudinary for starage.
The user is able to keep both the summarized  and the voice format of the text. This makes it possible to listen to your notes effortlessly.

## Use Cases
#### Education
 - With tiller, you only put effort on listening and understanding what the lecturer is teaching.
 - Tiller makes it possible to listen to your notes just like you would to music.
#### Solution for the deaf.
 - Tiller is a solution out of the box for people with hearing disability.
 With only a single click, the deaf can get all the information said in a meeting. 

 #### meetings and conferences.
 - In most meetings, most of the attendees never take notes, and it becomes difficult to refer to the information said in the future. With Tiller, you don't need to worry because everything is handled for you. 


## Accomplishments that am proud of
- Being able to develop an effective application that could literally solve my problem.
- Successfully integrating the frontend and the backend despite the many challenges i ran into.
- Learning some cool stuff through the implementation journey.

## What i learned
- I discovered that i could use the skills that i acquire to solve my own problems. 
 - I learnt more on how client-server integration works. Actually, this was my first experience integrating an api with a frontend.
- Containerizing the frontend, backend and database.
- Converting text to speech using the tiktok text to speech api
- Using github actions for rapid development and deployments.
## Built With

- **python and flask for the backend**
- **javascript, tailwind and react for the frontend**
- **postgresql database**
- **Tiktok text to speech api**
- **Cloudinary**
- **Google Speech recognition api**
- **Docker Compose for development**
- **Github Actions as the CI/CD pipeline**

<div align="center">
  <h1>How To Use Tiller </h1>
  <p> You can <b>fork or clone</b> the repository.</p> 
</div>

## Getting started

1. clone the respository
   ```shell
   $ git clone https://github.com/KariukiAntony/Tiller.git
   $ cd Tiller
   ```
2. Add the following variables to the .env file in the backend directory

   ```shell
   $ cd backend
   $ touch .env
   ```

   ```
   JWT_SECRET = 00044fe1-a7b7-460b-be33-d291ff1e1b31
   JWT_ALGORITHM = HS256
   JWT_TOKEN_EXPIRES = 1
   JWT_REFRESH_TOKEN_EXPIRES = 7
   SESSION_KEY = email
   REDIS_HOST = localhost
   REDIS_PORT = 6379
   CACHE_DEFAULT_TIMEOUT = 300
   logger_file=tiller.log
   MAIL_SERVER = smtp.gmail.com
   MAIL_PORT = 465
   MAIL_USE_SSL = True
   MAIL_USERNAME = [your mail username]
   MAIL_PASSWORD = [your mail password]
   FRONTEND_URL = [the frontend url]
   PORT = 5000

3. Add the following variables to the .env file in the frontend directory
   ```shell
   $ cd ..
   $ cd frontend
   $ touch .env
   ```
   ```
   JWT_SECRET = 00044fe1-a7b7-460b-be33-d291ff1e1b31
   ```

4. Spin up the containers
   - make sure you are in the root directory.
   ```shell
   $ docker compose up -d --build # if you are using a linux machine
   $ docker-compose up -d --build # If you are using a windows machine
   ```
5. Visit the frontend url: `http://localhost:5173`



## Contribution
Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request