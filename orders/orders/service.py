from nameko.exceptions import BadRequest
from nameko.events import EventDispatcher
from nameko.rpc import rpc
from nameko_sqlalchemy import DatabaseSession

from orders.exceptions import NotFound
from orders.models import DeclarativeBase, Test
from orders.schemas import TestSchema


class OrdersService:
    name = 'orders'

    db = DatabaseSession(DeclarativeBase)
    event_dispatcher = EventDispatcher()

    @rpc
    def get_test(self, test_id):
        test = self.db.query(Test).get(test_id)

        if not test:
            raise NotFound('Order with id {} not found'.format(test_id))

        return TestSchema().dump(test).data

    @rpc
    def create_test(self, data):
        # Validate input
        validated, errors = TestSchema().load(data)
        if errors:
            raise BadRequest("Validation failed: {}".format(errors))
        
        # Create Instance
        test = Test(
            name=validated['name'],
            age=validated['age']
        )
        
        # Add to db
        self.db.add(test)
        self.db.commit()

        # Serialize the instance
        testResult = TestSchema().dump(test).data

        # Dispatch event in Docker
        self.event_dispatcher('test_object_created', {
            'test_result': testResult,
        })

        # Return the serialized instance
        return testResult

    @rpc
    def update_test(self, test_id, data):
        # Validate input
        validated, errors = TestSchema().load(data)
        if errors:
            raise BadRequest("Validation failed: {}".format(errors))

        # Fetch the existing instance
        test = self.db.query(Test).get(test_id)

        # If not found, raise NotFound exception
        if not test:
            raise NotFound('Order with id {} not found'.format(data['id']))
        
        # Update the instance in db
        test.name = data['name']
        test.age = data['age']
        self.db.commit()
        
        # Return updated instance (serialized)
        return TestSchema().dump(test).data

    @rpc
    def delete_test(self, test_id):
        # Fetch targeted instance
        test = self.db.query(Test).get(test_id)
        
        # Delete in db
        self.db.delete(test)
        self.db.commit()
