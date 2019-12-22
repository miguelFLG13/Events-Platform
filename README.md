
# EVENT PLATFORM

En este documento me dispongo a explicar ciertos detalles de la implementación del código 

## Planteamiento

Antes de ponerme a picar código realicé una fase de análisis. Lo primero que hice fue leer unas cuantas veces el problema y de aquí obtuve el primer documento que está en la carpeta doc: el análisis de requisitos.
Mi segundo paso fue establecer los cimientos de la aplicación de una forma inicial, es decir, el modelo de datos. De esta forma, desde el principio podría tener de un vistazo una imagen de como conectan todos los conceptos dentro de la aplicación.
Lo siguiente fue definir el endpoint que necesitaría en el documento de definición de la API REST.
Finalmente, realice una breve descripción de los pasos que realizaría a la hora de implementar los dos requisitos, intentando emular lo que me explicasteis que hacíais el equipo de Fever.

## Docker-Compose

La forma más rápida de comenzar, siguiendo la afirmación de que no se pierda excesivo tiempo con docker, fue usar docker-compose con una receta que tenía en la que se incluyen varios servicios por si fuera necesario usarlos en el futuro.

Antes de usar el docker-compose se necesitarán inicializar varias variables de entorno:

```export WEB_ENVIRONMENT='LOCAL'
export DJANGO_SETTINGS_MODULE='event_platform.settings.local'
export SECRET_KEY='eHv60Lp4t&HM7NKwuAaUx%C30nUUtgbE)FOi4u0A7dw'
export DATABASE_NAME='postgres'
export DATABASE_USER='postgres'
export DATABASE_PASSWORD=''
export DATABASE_HOST='db'
```

Para usarlo tenemos un archivo Makefile con varios comandos, comentaré los más necesarios.

- make up: inicializa la aplicación levantando todo lo necesario y haciendo el build y coloca en http://localhost el desarrollo.
- make up-non-daemon: lo mismo que `make up` pero mostrando por pantalla el log.
- make run-tests: Corre la batería de tests completa realizada para esta aplicación.

## Modelo de datos

Intenté no acoplar el modelo de datos a la definición del XML que se me proporcionó ya que si se quiere escalar no sería una buena decisión. Se cambiaron ciertos detalles y se incluyó el concepto de ProviderResource para que él fuera el que se encargase de la parte de obtener los eventos de los Providers.

## Detalles

 - He dejado un Pull Request WIP preparado con comentarios con el Requirement 2 (RQ2) ya que no me ha dado tiempo a finalizarlo, faltaría la implementación del método adapt_resource en el modelo ProviderResource.
 - Creo que realmente solo se pedía realizar el que yo he definido como Requirement 1 (RQ1), pero bueno, me parece interesante lo que he implementado para la RQ2 ya que ha mejorado el modelo de datos para escalarlo.
 - He intentado, ya que es una prueba, simplificar lo máximo posible el planteamiento: he simplificado mucho el serializador del RQ1, un evento disponible es estar activo
 - Pienso que meter herencia a los eventos podía haber sido una buena idea para escalar mejor, pero tampoco me quería meter en el fregado teniendo 48hs. La idea sería localizar los tipos de eventos que hay y cada uno se comportará de una forma diferente aun teniendo cosas en común.
 - Estoy considerando que pueden modificar día a día los eventos y por eso al ejecutar la tarea se revisan los ya existentes en el RQ2

## Decisiones para escalar

 - El modelo de datos se concibió para que se pudiese escalar siendo totalmente flexible: Cada provider puede tener 0..* eventos, cada evento 0..* fechas y cada fecha 0..* zonas. Pero además, con las mejoras de la RQ2 se va a poder manejar mejor los eventos que cada provider facilita.
 - ProviderResource no solo es un modelo, además se encarga de ser un adaptador a la hora de obtener los eventos desde la url del provider para funcionar usando xml o json (pudiendo implementar nuevos tipos de archivo si se necesitase).
 - Otro de los objetivos de ProviderResource es que mediante un diccionario en el que se definirá la estructura del recurso que se obtiene del provider para poder procesarlo de forma automatizada ya que suponemos que cada provider enviara su recurso de una manera diferente. Esta es la parte de la RQ2 que me quedaría de implementar y me encantaría explicárosla en persona, aunque os dejo un ejemplo del formato del diccionario que tenía en la cabeza:
```
{
    'levels': [
        'base_event',
        'event',
        'zone'
    ],
    'provider_event_id': {
        'level': 1,
        'name': 'base_event_id'
    },
    'sale_start_date': {
        'level': 2,
        'sell_from': 'base_event_id'
    },
    ...
}
```
 - Se han cacheado los JSON que devuelve el endpoint con la idea de invalidar la caché cuando se modifique o añada algo al respecto, de esta manera solo se penaliza a la primera persona que solicita el recurso.