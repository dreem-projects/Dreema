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

<div align="left" style="max-width:720px; margin:0 auto; font-size:1.1rem; line-height:1.7;">
<p>
    <b>The current bottleneck in AI development isn't the AI—it’s the architecture.</b>
  </p>
  <p>
    While Large Language Models are exceptional at generating code, the systems they produce are often fragile, inconsistent, and difficult to maintain. Traditional frameworks were built for human-centric workflows, relying on deep tribal knowledge, complex boilerplate, and hidden side effects that confuse AI agents.
  </p>
  <p>
    When frameworks prioritize "magic" over predictability, AI agents struggle to generate code that is production-ready.
  </p>
  
</div>
</div>

---

<h1 style="margin-top: 10px; font-weight:600; font-size: 1.2rem; color:#563d7c;">
  Why Dreema?
</h1>

<p>
    <b>Dreema is a paradigm shift:</b> A Python framework architected specifically to be <i>AI-native</i>. By enforcing strict, predictable design patterns and standardized interfaces, Dreema ensures that AI-generated code is robust, modular, and natively compatible with automated workflows.
  </p>
  <p>
    <b>Stop fighting your framework. Start building with a foundation designed for the future of development using:
    </b>
  </p>

- **Dreem's batteries-included** ecosystem featuring ORMs, Middlewares, Plugs, etc.
- **Enforced Architecture:** Replaces flexible chaos with a deterministic MVC structure.
- **Universal Error Contract:** Delivers standardized responses that AI agents can reliably parse, debug, and self-heal.
- **Native AI tools:** Provides developers with AI tools for better developer experience.
- **Predictable Roadmap:** Provides the structural clarity AI needs to build, maintain, and scale systems with confidence.

---

<h1 style="margin-top: 10px; font-weight:600; font-size: 1.2rem; color:#563d7c;">
  Our Vision
</h1>
Dreema aims to redefine backend development by prioritizing both human intuition and AI efficiency. We provide the tools and structured architecture needed to build, maintain, and scale reliable backends that work seamlessly for both developers and AI agents.

<h1 style="margin-top: 10px; font-weight:600; font-size: 1.2rem; color:#563d7c;">
  Our Core Architecture
</h1>

<div style=" font-size:0.8rem; line-height:1.7;">

<h3 style="color:#563d7c;">1.  Enforced MVC Architecture</h3>
FastAPI is excellent for prototypes, but it lacks structural enforcement — leading to spaghetti code at scale. Dreema mandates a clean <b>Model-View-Controller</b> structure from day one leading to
<b>Zero Guesswork and AI Efficient </b> as developers and AI agents know where to look.

</div >
</p>

---

<h3 style="color:#563d7c;">2 . The Universal Response Contract</h3>

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

<h3 style="color:#563d7c;">3 . Unified ORM</h3>

Stop scaffolding database connections by hand. Dreema includes a powerful, database-agnostic ORM that lets you switch between storage engines.

**Write Once, Deploy Anywhere** &nbsp;—&nbsp; Business logic stays decoupled from the storage engine.

**Abstraction Done Right** &nbsp;—&nbsp; Dreema manages connections and dialect differences so you focus on your application.

---

<h1 style="margin-top: 10px; font-weight:600; font-size: 1.5rem; color:#563d7c;">
  Demo: Perform CRUD in 60seconds
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

⚠️ Warning: Not recommended for production; lacks the modularity needed for maintainable, scalable systems.

**Create a project**

```bash create dreema project: set --mode to core or full
dreema create project_name --mode core
cd project_name
```

**Create and define routes inside endpoint.py**

```python

  from dreema.routing import route
  from controllers.usersController import UsersController

  # routes can also be defined this way
  async def create():
      return {
          'data': {
              'name': 'Kweku Dreem'
          },
          "message": "Message sent",
          "status": 20
      }

  async def welcome():
      return "Welcome to Dreema"

  # register created route
  routes = [
          # creating single routes
          route.get('/welcome', welcome),
          route.post('/create', create),
  ]

```

**Start the server**

```bash
  dreema run .
```

## Style B - Installing with full mode (Recommended)

**Step 1 &mdash; Create your model**

```bash
dreema create-model userModel
```

```python
# app/models/user.py
from dreema.orm import database

class UserModel(database.Database):
    # change tablename here
    tablename = 'users'
```

**Step 2 &mdash; Create your controller**

```bash
dreema create-controller usersController
```

```python
# app/controllers/users.py
from dreema import Request
from app.models.user import UsersModel

class UsersController:

  @staticmethod
  async def createUser(request: Request):
      # Validate the incoming body
      body = await request.apply_rules({
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

**Step 2 &mdash; Register endpoint**

```python
# app/view/endpoint.py
from dreema.routing import route, routegroup
import controllers.users as UsersController

"""
        author:  Raphael Djangmah
        Use:
                This file is the main view entry.
"""
routes = [
        # creating single routes
        route.post('/create-user', UsersController.createUser),
  ]
```

**Step 5 &mdash; Start the server**

```bash
  dreema run .
```

**Step 6 &mdash; Call the endpoint**

```bash
curl -X POST http://localhost:8000/create-user \
  -H "Content-Type: application/json" \
  -d '{"name": "Jane Doe", "email": "jane@example.com"}'
```

<b>Response — always this shape, always.</b>

- If validation failed

```json
{
  "data": Null,
  "message": "Attribute is missing",
  "status": -30
}
```

- If validation succeeded

```json
{
  "data": { "id": 1, "name": "Jane Doe", "email": "jane@example.com" },
  "message": "Create operation successful",
  "status": 22
}
```

Routing, validation, ORM, and response formatting — all handled, all consistent.

<div align="center">

<img src="https://img.shields.io/badge/Dreema-Convention%20Over%20Configuration-563d7c?style=for-the-badge" alt="Convention Over Configuration" />

<!-- <p style="margin-top:1rem;">
<a href="https://dreem-projects.github.io/dq-docs/v1/" style="color:#563d7c; font-weight:bold;">View Full Documentation</a>
&nbsp;·&nbsp;
<a href="v1/" style="color:#563d7c; font-weight:bold;">Current Version (v1)</a>
</p> -->

</div>
