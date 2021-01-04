
import json

from django.core import exceptions, serializers
from django.db import IntegrityError
from django.test import (
    SimpleTestCase, TestCase, TransactionTestCase, skipUnlessDBFeature,
)


from standards.tests.models import (
    CharIdModel,
    CharIdModelWithPrefix,
    NullableCharIdModel,
    PrimaryKeyCharIdModel,
    RelatedToCharIdModel,
    CharIdGrandchildModel
)
from standards.fields import CharIdField



# MODEL FIELD TESTS
# https://github.com/django/django/blob/master/tests/model_fields/test_uuid.py
################################################################################

class TestSaveLoad(TestCase):
    def test_uuid_instance(self):
        instance = CharIdModel.objects.create(field="astringid")
        loaded = CharIdModel.objects.get()
        self.assertEqual(loaded.field, instance.field)

    def test_str_instance_no_hyphens(self):
        CharIdModel.objects.create(field='khLnNzX')
        loaded = CharIdModel.objects.get()
        self.assertEqual(loaded.field, 'khLnNzX')

    def test_null_handling(self):
        NullableCharIdModel.objects.create(field=None)
        loaded = NullableCharIdModel.objects.get()
        self.assertIsNone(loaded.field)

    # def test_pk_validated(self):
    #     with self.assertRaisesMessage(exceptions.ValidationError, 'is not a valid char id'):
    #         PrimaryKeyCharIdModel.objects.get(pk=33)
    #
    #     with self.assertRaisesMessage(exceptions.ValidationError, 'is not a valid char id'):
    #         PrimaryKeyCharIdModel.objects.get(pk=[])
    #
    # def test_wrong_value(self):
    #     with self.assertRaisesMessage(exceptions.ValidationError, 'is not a valid char id'):
    #         CharIdModel.objects.get(field='01')
    #
    #     with self.assertRaisesMessage(exceptions.ValidationError, 'is not a valid char id'):
    #         CharIdModel.objects.create(field='01')


class TestSaveLoadWithPrefix(TestCase):

    def test_auto_generated(self):
        instance = CharIdModelWithPrefix.objects.create()
        loaded = CharIdModelWithPrefix.objects.get()
        self.assertEqual(loaded.field[0:2], 'WP')
        self.assertEqual(loaded.field, instance.field)

    def test_manual_field_shorter_than_expected(self):
        CharIdModelWithPrefix.objects.create(field='WPkhLnNzX')
        loaded = CharIdModelWithPrefix.objects.get()
        self.assertEqual(loaded.field, 'WPkhLnNzX')

    def test_manual_field(self):
        CharIdModelWithPrefix.objects.create(field='WPhxFQDpJdcv')
        loaded = CharIdModelWithPrefix.objects.get()
        self.assertEqual(loaded.field, 'WPhxFQDpJdcv')
        self.assertEqual(loaded.field[0:2], 'WP')


class TestMethods(SimpleTestCase):

    def test_deconstruct(self):
        field = CharIdField()
        name, path, args, kwargs = field.deconstruct()
        self.assertIn('length', kwargs.keys())

class TestQuerying(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.objs = [
            NullableCharIdModel.objects.create(field='2JnqMHW'),
            NullableCharIdModel.objects.create(field='JymifvX'),
            NullableCharIdModel.objects.create(field=None),
        ]

    def test_exact(self):
        self.assertSequenceEqual(
            NullableCharIdModel.objects.filter(field__exact='JymifvX'),
            [self.objs[1]]
        )
        self.assertSequenceEqual(
            NullableCharIdModel.objects.filter(field__exact='JymifvX'),
            [self.objs[1]],
        )

    def test_isnull(self):
        self.assertSequenceEqual(
            NullableCharIdModel.objects.filter(field__isnull=True),
            [self.objs[2]]
        )



class TestSerialization(SimpleTestCase):
    test_data = (
        '[{"fields": {"field": "JymifvX"}, '
        '"model": "standards_tests.charidmodel", "pk": null}]'
    )
    nullable_test_data = (
        '[{"fields": {"field": null}, '
        '"model": "standards_tests.nullablecharidmodel", "pk": null}]'
    )

    def test_dumping(self):
        instance = CharIdModel(field='JymifvX')
        data = serializers.serialize('json', [instance])
        self.assertEqual(json.loads(data), json.loads(self.test_data))

    def test_loading(self):
        instance = list(serializers.deserialize('json', self.test_data))[0].object
        self.assertEqual(instance.field, 'JymifvX')

    def test_nullable_loading(self):
        instance = list(serializers.deserialize('json', self.nullable_test_data))[0].object
        self.assertIsNone(instance.field)



# class TestValidation(SimpleTestCase):
#     def test_invalid_uuid(self):
#         field = CharIdField()
#         with self.assertRaises(exceptions.ValidationError) as cm:
#             field.clean('01', None)
#         self.assertEqual(cm.exception.code, 'invalid')
#         # self.assertEqual(cm.exception.message % cm.exception.params, 'is not a valid char id')
#
#     def test_uuid_instance_ok(self):
#         field = CharIdField()
#         field.clean('JymifvX', None)  # no error



class TestAsPrimaryKey(TestCase):
    def test_creation(self):
        PrimaryKeyCharIdModel.objects.create()
        loaded = PrimaryKeyCharIdModel.objects.get()
        self.assertIsInstance(loaded.pk, str)

    def test_uuid_pk_on_save(self):
        saved = PrimaryKeyCharIdModel.objects.create(id=None)
        loaded = PrimaryKeyCharIdModel.objects.get()
        self.assertIsNotNone(loaded.id, None)
        self.assertEqual(loaded.id, saved.id)

    def test_uuid_pk_on_bulk_create(self):
        u1 = PrimaryKeyCharIdModel()
        u2 = PrimaryKeyCharIdModel(id=None)
        PrimaryKeyCharIdModel.objects.bulk_create([u1, u2])
        # The two objects were correctly created.
        u1_found = PrimaryKeyCharIdModel.objects.filter(id=u1.id).exists()
        u2_found = PrimaryKeyCharIdModel.objects.exclude(id=u1.id).exists()
        self.assertTrue(u1_found)
        self.assertTrue(u2_found)
        self.assertEqual(PrimaryKeyCharIdModel.objects.count(), 2)

    def test_underlying_field(self):
        pk_model = PrimaryKeyCharIdModel.objects.create()
        RelatedToCharIdModel.objects.create(char_fk=pk_model)
        related = RelatedToCharIdModel.objects.get()
        self.assertEqual(related.char_fk.pk, related.char_fk_id)

    def test_update_with_related_model_instance(self):
        u1 = PrimaryKeyCharIdModel.objects.create()
        u2 = PrimaryKeyCharIdModel.objects.create()
        r = RelatedToCharIdModel.objects.create(char_fk=u1)
        RelatedToCharIdModel.objects.update(char_fk=u2)
        r.refresh_from_db()
        self.assertEqual(r.char_fk, u2)

    def test_update_with_related_model_id(self):
        u1 = PrimaryKeyCharIdModel.objects.create()
        u2 = PrimaryKeyCharIdModel.objects.create()
        r = RelatedToCharIdModel.objects.create(char_fk=u1)
        RelatedToCharIdModel.objects.update(char_fk=u2.pk)
        r.refresh_from_db()
        self.assertEqual(r.char_fk, u2)

    def test_two_level_foreign_keys(self):
        gc = CharIdGrandchildModel()
        # exercises ForeignKey.get_db_prep_value()
        gc.save()
        self.assertIsInstance(gc.primarykeycharidmodel_ptr_id, str)
        gc.refresh_from_db()
        self.assertIsInstance(gc.primarykeycharidmodel_ptr_id, str)



class TestAsPrimaryKeyTransactionTests(TransactionTestCase):
    # Need a TransactionTestCase to avoid deferring FK constraint checking.

    @skipUnlessDBFeature('supports_foreign_keys')
    def test_unsaved_fk(self):
        u1 = PrimaryKeyCharIdModel()
        with self.assertRaises(IntegrityError):
            RelatedToCharIdModel.objects.create(char_fk=u1)


# CUSTOM FORM FIELD ?
# https://github.com/django/django/blob/master/django/forms/fields.py#L1189-L1208
# https://github.com/django/django/blob/master/tests/forms_tests/field_tests/test_uuidfield.py#L8
