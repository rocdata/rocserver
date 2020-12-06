from functools import partial

import json
import uuid

from django.core import exceptions, serializers
from django.db import IntegrityError, connection, models
from django.db.models import CharField, F, Value
from django.db.models.functions import Concat, Repeat
from django.test import (
    SimpleTestCase, TestCase, TransactionTestCase, skipUnlessDBFeature,
)


from standards.tests.models import (
    UUIDModel,
    NullableUUIDModel,
    PrimaryKeyUUIDModel,
    RelatedToUUIDModel,
    UUIDChild,
    UUIDGrandchild
)
from standards.utils import ShortUUIDField, generate_short_code
from standards.utils import short_code_to_uuid, uuid_to_short_code



# MODEL FIELD TESTS
# https://github.com/django/django/blob/master/tests/model_fields/test_uuid.py
################################################################################

class TestSaveLoad(TestCase):
    def test_uuid_instance(self):
        instance = UUIDModel.objects.create(field=generate_short_code())
        loaded = UUIDModel.objects.get()
        self.assertEqual(loaded.field, instance.field)

    def test_str_instance_no_hyphens(self):
        UUIDModel.objects.create(field='khLnNzX')
        loaded = UUIDModel.objects.get()
        self.assertEqual(loaded.field, 'khLnNzX')
        self.assertEqual(short_code_to_uuid(loaded.field), uuid.UUID('00000000-0000-0000-0000-0154e40df060'))

    def test_null_handling(self):
        NullableUUIDModel.objects.create(field=None)
        loaded = NullableUUIDModel.objects.get()
        self.assertIsNone(loaded.field)

    def test_pk_validated(self):
        with self.assertRaisesMessage(exceptions.ValidationError, 'is not a valid shortuuid'):
            PrimaryKeyUUIDModel.objects.get(pk=33)

        with self.assertRaisesMessage(exceptions.ValidationError, 'is not a valid shortuuid'):
            PrimaryKeyUUIDModel.objects.get(pk=[])

    def test_wrong_value(self):
        with self.assertRaisesMessage(exceptions.ValidationError, 'is not a valid shortuuid'):
            UUIDModel.objects.get(field='01')

        with self.assertRaisesMessage(exceptions.ValidationError, 'is not a valid shortuuid'):
            UUIDModel.objects.create(field='01')



class TestMethods(SimpleTestCase):

    def test_deconstruct(self):
        field = ShortUUIDField()
        name, path, args, kwargs = field.deconstruct()
        self.assertIn('default', kwargs.keys())

    def test_to_python(self):
        self.assertIsNone(ShortUUIDField().to_python(None))

    def test_to_python_int_values(self):
        uuid_value = ShortUUIDField().to_python('3')
        self.assertEqual(uuid_value, '3')
        self.assertEqual(
            short_code_to_uuid(uuid_value),
            uuid.UUID('00000000-0000-0000-0000-000000000001'))
        # Works for integers less than 128 bits.
        self.assertEqual(
            short_code_to_uuid(ShortUUIDField().to_python('oZEq7ovRbLq6UnGMPwc8B5')),
            uuid.UUID('ffffffff-ffff-ffff-ffff-ffffffffffff')
        )

    def test_to_python_int_too_large(self):
        # Fails for integers larger than 128 bits.
        with self.assertRaises(exceptions.ValidationError):
            models.UUIDField().to_python('oZEq7ovRbLq6UnGMPwc8B5a')


class TestQuerying(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.objs = [
            NullableUUIDModel.objects.create(field='2JnqMHW'),
            NullableUUIDModel.objects.create(field='JymifvX'),
            NullableUUIDModel.objects.create(field=None),
        ]

    def test_exact(self):
        self.assertSequenceEqual(
            NullableUUIDModel.objects.filter(field__exact='JymifvX'),
            [self.objs[1]]
        )
        self.assertSequenceEqual(
            NullableUUIDModel.objects.filter(field__exact='JymifvX'),
            [self.objs[1]],
        )

    def test_isnull(self):
        self.assertSequenceEqual(
            NullableUUIDModel.objects.filter(field__isnull=True),
            [self.objs[2]]
        )


class TestSerialization(SimpleTestCase):
    test_data = (
        '[{"fields": {"field": "JymifvX"}, '
        '"model": "standards_tests.uuidmodel", "pk": null}]'
    )
    nullable_test_data = (
        '[{"fields": {"field": null}, '
        '"model": "standards_tests.nullableuuidmodel", "pk": null}]'
    )

    def test_dumping(self):
        instance = UUIDModel(field='JymifvX')
        data = serializers.serialize('json', [instance])
        self.assertEqual(json.loads(data), json.loads(self.test_data))

    def test_loading(self):
        instance = list(serializers.deserialize('json', self.test_data))[0].object
        self.assertEqual(instance.field, 'JymifvX')

    def test_nullable_loading(self):
        instance = list(serializers.deserialize('json', self.nullable_test_data))[0].object
        self.assertIsNone(instance.field)


class TestValidation(SimpleTestCase):
    def test_invalid_uuid(self):
        field = ShortUUIDField()
        with self.assertRaises(exceptions.ValidationError) as cm:
            field.clean('01', None)
        self.assertEqual(cm.exception.code, 'invalid')
        # self.assertEqual(cm.exception.message % cm.exception.params, 'is not a valid shortuuid')

    def test_uuid_instance_ok(self):
        field = ShortUUIDField()
        field.clean('JymifvX', None)  # no error


class TestAsPrimaryKey(TestCase):
    def test_creation(self):
        PrimaryKeyUUIDModel.objects.create()
        loaded = PrimaryKeyUUIDModel.objects.get()
        self.assertIsInstance(loaded.pk, str)

    def test_uuid_pk_on_save(self):
        saved = PrimaryKeyUUIDModel.objects.create(id=None)
        loaded = PrimaryKeyUUIDModel.objects.get()
        self.assertIsNotNone(loaded.id, None)
        self.assertEqual(loaded.id, saved.id)

    def test_uuid_pk_on_bulk_create(self):
        u1 = PrimaryKeyUUIDModel()
        u2 = PrimaryKeyUUIDModel(id=None)
        PrimaryKeyUUIDModel.objects.bulk_create([u1, u2])
        # The two objects were correctly created.
        u1_found = PrimaryKeyUUIDModel.objects.filter(id=u1.id).exists()
        u2_found = PrimaryKeyUUIDModel.objects.exclude(id=u1.id).exists()
        self.assertTrue(u1_found)
        self.assertTrue(u2_found)
        self.assertEqual(PrimaryKeyUUIDModel.objects.count(), 2)

    def test_underlying_field(self):
        pk_model = PrimaryKeyUUIDModel.objects.create()
        RelatedToUUIDModel.objects.create(uuid_fk=pk_model)
        related = RelatedToUUIDModel.objects.get()
        self.assertEqual(related.uuid_fk.pk, related.uuid_fk_id)

    def test_update_with_related_model_instance(self):
        # regression for #24611
        u1 = PrimaryKeyUUIDModel.objects.create()
        u2 = PrimaryKeyUUIDModel.objects.create()
        r = RelatedToUUIDModel.objects.create(uuid_fk=u1)
        RelatedToUUIDModel.objects.update(uuid_fk=u2)
        r.refresh_from_db()
        self.assertEqual(r.uuid_fk, u2)

    def test_update_with_related_model_id(self):
        u1 = PrimaryKeyUUIDModel.objects.create()
        u2 = PrimaryKeyUUIDModel.objects.create()
        r = RelatedToUUIDModel.objects.create(uuid_fk=u1)
        RelatedToUUIDModel.objects.update(uuid_fk=u2.pk)
        r.refresh_from_db()
        self.assertEqual(r.uuid_fk, u2)

    def test_two_level_foreign_keys(self):
        gc = UUIDGrandchild()
        # exercises ForeignKey.get_db_prep_value()
        gc.save()
        self.assertIsInstance(gc.uuidchild_ptr_id, str)
        gc.refresh_from_db()
        self.assertIsInstance(gc.uuidchild_ptr_id, str)


class TestAsPrimaryKeyTransactionTests(TransactionTestCase):
    # Need a TransactionTestCase to avoid deferring FK constraint checking.

    @skipUnlessDBFeature('supports_foreign_keys')
    def test_unsaved_fk(self):
        u1 = PrimaryKeyUUIDModel()
        with self.assertRaises(IntegrityError):
            RelatedToUUIDModel.objects.create(uuid_fk=u1)


# CUSTOM FORM FIELD ?
# https://github.com/django/django/blob/master/django/forms/fields.py#L1189-L1208
# https://github.com/django/django/blob/master/tests/forms_tests/field_tests/test_uuidfield.py#L8
