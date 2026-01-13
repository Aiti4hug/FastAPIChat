from fastapi import FastAPI
import uvicorn
from mysite.api import auth, people, group, user

app = FastAPI()

app.include_router(auth.auth_router)
app.include_router(user.user_router)
app.include_router(group.group_router)
app.include_router(people.people_router)


if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8000)