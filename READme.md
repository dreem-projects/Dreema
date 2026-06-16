<div align="center">

<img src="https://img.shields.io/badge/Dreema-Python%20Backend-5B3DF5?style=for-the-badge&logo=python" alt="Dreema Python Backend" />

<p style="margin:6px 0 10px 0;">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/License-MIT-22c55e?style=flat-square" />
  <img src="https://img.shields.io/badge/Status-Beta-f59e0b?style=flat-square" />
  <img src="https://img.shields.io/badge/AI--First-Architecture-5B3DF5?style=flat-square" />
</p>

<h1 style="margin: 6px 0 0 0; font-size: 2.5rem; color:#563d7c;">
   Build Backend Systems That Scale
</h1>

<p style="margin:6px 0 14px 0; font-size:1.15rem; font-weight:400; color:#563d7c;">
  • Structure • Consistency • AI-ready systems
</p>

<p style="margin-top:1rem;">
<a href="https://discord.gg/fTkjpq4Epm" style="color:#563d7c; text-decoration: underline; font-weight:bold;">
  <u>Join Our Community</u>
</a>
</p>

<div align="left" style="max-width:720px; margin:0 auto; font-size:1.1rem; line-height:1.7;">
<div style="padding: 20px; border-left: 4px solid #563d7c;">
  <b>The bottleneck in AI-assisted development isn't the AI—it’s the architecture on which it is forced to build.</b>
  <p >
    Traditional frameworks rely on "magic" and hidden side effects that results in fragile, unmaintainable code. <b>Dreema</b> replaces this chaos with <b>structural certainty</b>. 
  </p>
  <p>
    By enforcing a deterministic MVC pattern and a universal response contract across all internal function as well as ready to use ORM, plugs, middlewares, etc, Dreema provides the clarity developers need to build, and the predictable interface AI agents require to scale systems reliably.
  </p>
</div>
  
</div>
</div>

---

<h1 style="margin-top: 10px; font-weight:600; font-size: 1.2rem; color:#563d7c;">
  Why Dreema?
</h1>

<p>
    <b>Dreema is a paradigm shift:</b> A Python framework architected specifically to write scalable and support AI-assistive development. By enforcing strict, predictable design patterns and standardized interfaces, Dreema ensures that developers and AI-generated code is robust, modular, and natively compatible with automated workflows.
  </p>

---

<h1 style="margin-top: 10px; font-weight:500; font-size: 1.5rem; color:#563d7c;">
  Build production ready endpoints
</h1>

**Setup and Installation**

```bash
# setup and activate virtual environment
python -m venv venv
source venv/bin/activate

#install dreema
pip install dreema

```

### Choose Your Style

<div>Building high-performance endpoints with Dreema is designed to be intuitive. Choose the approach that fits your project needs.</div>

## Style A - Core Mode (Minimalistic)

Best for microservices or simple API routes. This setup provides a single entry point for all your logic.

⚠️ Best for rapid prototyping and micro-services; transition to Full Mode for production-grade scalability."

**Create a project**

```bash create dreema project: set --mode to core or full
dreema create-project <project_name> --mode core
cd <project_name>

dreema run
```

**Test in browser or curl**

````bash
curl -X POST http://localhost:<port/>

#Response — always this shape, (data, message and status)

```json
{
  "data": Null,
  "message": "Welcome",
  "status": 100
}
````

#### Project Structure

**endpoint**
Adjust this file according to your needs and register all functions into the _routes_ array

```python
# app/view/endpoint.py
from dreema.routing import route
from dreema.responses import SysCodes, response, SysMessages

async def userRead():
    {
        'data': {
            'name': 'Qweku Dreem'
        },
        "message": "Message sent",
        "status": 20
    }

async def welcome():
    # using standard response envelope
    return response(data=None, message=SysMessages.SETUP_COMPLETED, status=SysCodes.SETUP_COMPLETED)


# define your route here
routes = [
        # get, post, put, delete for single routes
        route.get('/',welcome),

        # grouping multiple routes
        route.group('/users', [
            route.get('/read', userRead)
        ]),
]
```

---

## Style B - Full mode (Recommended)

<p style="margin-top: 10px; font-weight:200; font-size: 1.5rem; color:#56397c;">
Perform Database Operations in seconds
</p>

#### Setup and run

```bash create dreema project: --mode full (by default)
#
dreema create-project <project_name>
cd <project_name>

#run the project
dreema run
```

### Project Structure

#### add database details in .env

```bash
  # default db settings
  DB_TYPE=mongo
  DB_HOST=
  DB_PORT=
  DB_NAME=
  DB_USER=
  DB_PASSWORD=

```

#### models

```python
# app/models/user.py
from dreema.orm import database

class UserModel(database.Database):
    # change tablename here
    tablename = 'users'
```

```bash
# terminal command to creating more models
dreema create-model <controller_name>
```

#### controllers

```python
# app/controllers/users.py
from dreema import Request
from app.models.user import UsersModel

class UsersController:

  @staticmethod
  async def createUser(request: Request):
      # Validate the incoming body
      body = await request.applyRules({
          "name": "string,required",
          "email": "email,required"
      })

      # Short-circuit on validation failure
      if body.status < 0:
          return body

      # Create the record
      model = UsersModel()
      user = await User.create({
          "name": body.data.name,
          "email": body.data.email,
      })

      return user
```

```bash
# terminal command to creating more controllers
dreema create-controller <controller_name>
```

#### views

_Empty by default_

#### Register routes into endpoint

```python
#endpoint.py

from dreema.routing import route
from controllers.usersController import UsersController


# defining all routes coming from the controllers
routes = [
        # creating single routes
        route.get('/welcome', UsersController.welcome),

        # create grouped routes
        route.group('/users', [
            route.get('/read', UsersController.testRead),
            route.post('/create', UsersController.testCreate)
        ]),

        # routes with multiple methods
        route(path="/", methods=["GET", "POST"], handler=UsersController.welcome),
]

```

<h1 style="margin-top: 10px; font-weight:600; font-size: 1.2rem; color:#563d7c;">
  Our Vision
</h1>
Dreema aims to redefine backend development by prioritizing both human intuition and AI efficiency. We provide the tools and structured architecture needed to build, maintain, and scale reliable backends that work seamlessly for both developers and AI agents.

<h1 style="margin-top: 40px; font-weight:600; font-size: 1.2rem; color:#563d7c;">
  Our Core Architecture
</h1>

<div>

### 1. Enforced MVC Architecture</h3>

FastAPI is excellent for prototypes, but it lacks structural enforcement — leading to spaghetti code at scale. Dreema mandates a clean <b>Model-View-Controller</b> structure from day one leading to
<b>Zero Guesswork and AI Efficient </b> as developers and AI agents know where to look.

</div >
</p>

---

### 2 . The Universal Response Contract</h3>

System fragility is the enemy of automation. Dreema implements a strict, fixed response schema for every request — internal or external. This provides a predictable contract that AI agents can rely on to diagnose, debug, and self-heal.

<table>
<tr>
<td width="50%" valign="top">

#Success

```json
{
  "data": { "id": 1, "name": "Jane Doe" },
  "message": "User created successfully",
  "status": 21
}
```

</td>
<td width="50%" valign="top">

**Failure**

```json
{
  "data": null,
  "message": "Validation failed: email required",
  "status": 21
}
```

</td>
</tr>
</table>

No controller-specific error formats. No guessing what shape a failure takes. Every response is machine-readable by design.

---

### 3 . Unified ORM</h3>

Stop scaffolding database connections by hand. Dreema includes a powerful, database-agnostic ORM that lets you switch between storage engines.

**Write Once, Deploy Anywhere** &nbsp;—&nbsp; Business logic stays decoupled from the storage engine.

**Abstraction Done Right** &nbsp;—&nbsp; Dreema manages connections and dialect differences so you focus on your application.

Routing, validation, ORM, and response formatting — all handled, all consistent.
Dreema is the new age backend framework that combines into one the:

- Structure of Laravel
- Speed of FastAPI
- Battery inclusion of Django
- Comfort of Express.js
- Professionalism of Springboot
- etc
<div align="center">

<p style="margin-top:1rem;">
<a href="https://discord.gg/fTkjpq4Epm" style="color:#563d7c; font-weight:bold;">Join our discord community</a>
&nbsp;·&nbsp;
<a href="https://dreem-projects.github.io/dq-docs/v1/" style="color:#563d7c; font-weight:bold;">Full documentation</a>
</p>

<img src="https://img.shields.io/badge/Dreema-Convention%20Over%20Configuration-563d7c?style=for-the-badge" alt="Convention Over Configuration" />
</div>
