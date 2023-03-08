from pathlib import Path
from boa3_test.tests.boa_test import BoaTest
from boa3_test.tests.test_classes.testengine import TestEngine
from boa3.neo.smart_contract.VoidType import VoidType
from boa3.neo.cryptography import hash160
from boa3.constants import GAS_SCRIPT
from boa3.neo import to_script_hash, to_hex_str
from boa3.builtin.type import UInt160, ByteString
from boa3_test.tests.test_classes.TestExecutionException import TestExecutionException
from boa3_test.tests.test_classes.testcontract import TestContract


class NEP11Test(BoaTest):
    p = Path(__file__)
    NEP11_ROOT = str(p.parents[1])
    PRJ_ROOT = str(p.parents[2])

    CONTRACT_PATH_JSON = NEP11_ROOT+ '/contracts/NEP11/NEP11-Template.manifest.json'
    CONTRACT_PATH_NEF = NEP11_ROOT + '/contracts/NEP11/NEP11-Template.nef'
    CONTRACT_PATH_PY = NEP11_ROOT + '/contracts/NEP11/NEP11-Template.py'
    TEST_ENGINE_PATH = '%s/neo-devpack-dotnet/src/Neo.TestEngine/bin/Debug/net6.0' % NEP11_ROOT
    BOA_PATH = PRJ_ROOT + '/neo3-boa/boa3'
    OWNER_SCRIPT_HASH = UInt160(to_script_hash(b'NZcuGiwRu1QscpmCyxj5XwQBUf6sk7dJJN'))
    OTHER_ACCOUNT_1 = UInt160(to_script_hash(b'NiNmXL8FjEUEs1nfX9uHFBNaenxDHJtmuB'))
    OTHER_ACCOUNT_2 = bytes(range(20))
    TOKEN_META = bytes('{ "name": "NEP11", "description": "Some description", "image": "{some image URI}", "tokenURI": "{some URI}" }', 'utf-8')
    LOCK_CONTENT = bytes('lockedContent', 'utf-8')
    ROYALTIES = bytes('[{"address": "NZcuGiwRu1QscpmCyxj5XwQBUf6sk7dJJN", "value": 200}, {"address": "NiNmXL8FjEUEs1nfX9uHFBNaenxDHJtmuB", "value": 300}]', 'utf-8')
    ROYALTIES_BOGUS = bytes('[{"addresss": "someaddress", "value": "20"}, {"address": "someaddress2", "value": "30"}]', 'utf-8')
    CONTRACT = UInt160()

    def build_contract(self, preprocess=False):
        print('contract path: ' + self.CONTRACT_PATH_PY)
        if preprocess:
            import os
            old = os.getcwd()
            os.chdir(self.GHOST_ROOT)
            file = self.GHOST_ROOT + '/compile.py'
            os.system(file)
            os.chdir(old)
        else:
            output, manifest = self.compile_and_save(self.CONTRACT_PATH_PY)
            self.CONTRACT = hash160(output)

    def deploy_contract(self, engine):
        cc = TestContract(self.CONTRACT_PATH_NEF, self.CONTRACT_PATH_JSON)
        # engine.add_contract(self.CONTRACT_PATH_NEF.replace('.py', '.nef'))
        engine.add_signer_account(self.OWNER_SCRIPT_HASH)
        result = self.run_smart_contract(engine, self.CONTRACT_PATH_NEF, '_deploy', self.OWNER_SCRIPT_HASH, False,
                                         signer_accounts=[self.OWNER_SCRIPT_HASH],
                                         expected_result_type=bool)
        storage = engine.storage.to_json()
        #for i in range(0, len(storage)):
        #    print(storage[i])
        #self.assertEqual(VoidType, result)

    def prepare_testengine(self, preprocess=False) -> TestEngine:
        engine = TestEngine(self.TEST_ENGINE_PATH)
        engine.reset_engine()
        
        self.deploy_contract(engine)
        return engine

    def print_notif(self, notifications):
        print('\n=========================== NOTIFICATIONS START ===========================\n')
        for notif in notifications:
            print(f"{str(notif.name)}: {str(notif.arguments)}")
        print('\n=========================== NOTIFICATIONS END ===========================\n')

    def test_nep11_compile(self):
        self.build_contract()

    def test_nep11_symbol(self):
        engine = self.prepare_testengine()
        result = engine.run(self.CONTRACT_PATH_NEF, 'symbol', reset_engine=True)
        self.print_notif(engine.notifications)

        assert isinstance(result, str)
        assert result == 'EXMP'

    def test_nep11_decimals(self):
        engine = self.prepare_testengine()
        result = engine.run(self.CONTRACT_PATH_NEF, 'decimals', reset_engine=True)
        self.print_notif(engine.notifications)

        assert isinstance(result, int)
        assert result == 0

    def test_nep11_total_supply(self):
        engine = self.prepare_testengine()
        result = engine.run(self.CONTRACT_PATH_NEF, 'totalSupply', reset_engine=True)
        self.print_notif(engine.notifications)

        assert isinstance(result, int)
        assert result == 0

    def test_nep11_deploy(self):
        engine = self.prepare_testengine()
        # prepare_testengine already deploys the contract and verifies it's successfully deployed

        result = self.run_smart_contract(engine, self.CONTRACT_PATH_NEF, '_deploy', None, False,
                                             signer_accounts=[self.OWNER_SCRIPT_HASH],
                                         expected_result_type=bool)
        self.print_notif(engine.notifications)

    def test_nep11_update(self):
        engine = self.prepare_testengine()

        # updating EXMP smart contract
        file_script = open(self.CONTRACT_PATH_NEF, 'rb')
        script = file_script.read()
        #print(script)
        file_script.close()

        file_manifest = open(self.CONTRACT_PATH_JSON, 'rb')
        manifest = file_manifest.read()
        #print(manifest)
        file_manifest.close()

        result = self.run_smart_contract(engine, self.CONTRACT_PATH_NEF, 'update', 
                                         script, manifest,
                                         signer_accounts=[self.OWNER_SCRIPT_HASH],
                                         expected_result_type=bool)
        self.assertEqual(VoidType, result)

    def test_nep11_destroy(self):
        engine = self.prepare_testengine()

        # destroy contract
        result = self.run_smart_contract(engine, self.CONTRACT_PATH_NEF, 'destroy',
                                         signer_accounts=[self.OWNER_SCRIPT_HASH],
                                         expected_result_type=bool)

        # should not exist anymore
        result = self.run_smart_contract(engine, self.CONTRACT_PATH_NEF, 'symbol')
        self.assertNotEqual('', result)

        self.print_notif(engine.notifications)

    def test_nep11_verify(self):
        engine = self.prepare_testengine()

        # should fail because account does not have enough for fees
        verified = self.run_smart_contract(engine, self.CONTRACT_PATH_NEF, 'verify',
                signer_accounts=[self.OTHER_ACCOUNT_2],
                expected_result_type=bool)
        self.assertEqual(verified, False)

        addresses = self.run_smart_contract(engine, self.CONTRACT_PATH_NEF, 'getAuthorizedAddress',
                expected_result_type=list[UInt160],
                signer_accounts=[self.OWNER_SCRIPT_HASH])
        print(addresses)
        self.assertEqual(addresses[0], self.OWNER_SCRIPT_HASH)
        self.assertEqual(len(addresses), 1)

        verified = self.run_smart_contract(engine, self.CONTRACT_PATH_NEF, 'verify',
                signer_accounts=[self.OTHER_ACCOUNT_1],
                expected_result_type=bool)
        self.assertEqual(verified, False)

        verified = self.run_smart_contract(engine, self.CONTRACT_PATH_NEF, 'verify',
                signer_accounts=[self.OTHER_ACCOUNT_2],
                expected_result_type=bool)
        self.assertEqual(verified, False)

        verified = self.run_smart_contract(engine, self.CONTRACT_PATH_NEF, 'verify',
                signer_accounts=[self.OWNER_SCRIPT_HASH],
                expected_result_type=bool)
        self.assertEqual(verified, True)

        self.print_notif(engine.notifications)

    def test_nep11_authorize_2(self):
        engine = self.prepare_testengine()
        self.run_smart_contract(engine, self.CONTRACT_PATH_NEF, 'setAuthorizedAddress', 
                self.OTHER_ACCOUNT_1, True,
                signer_accounts=[self.OWNER_SCRIPT_HASH],
                expected_result_type=bool)
        auth_events = engine.get_events('Authorized')

        # check if the event was triggered and the address was authorized
        self.assertEqual(0, auth_events[0].arguments[1])
        self.assertEqual(1, auth_events[0].arguments[2])

        # now deauthorize the address
        self.run_smart_contract(engine, self.CONTRACT_PATH_NEF, 'setAuthorizedAddress', 
                self.OTHER_ACCOUNT_1, False,
                signer_accounts=[self.OWNER_SCRIPT_HASH],
                expected_result_type=bool)
        auth_events = engine.get_events('Authorized')
        # check if the event was triggered and the address was authorized
        self.assertEqual(0, auth_events[1].arguments[1])
        self.assertEqual(0, auth_events[1].arguments[2])

    def test_nep11_authorize(self):
        engine = self.prepare_testengine()
        self.run_smart_contract(engine, self.CONTRACT_PATH_NEF, 'setAuthorizedAddress', 
                self.OTHER_ACCOUNT_1, True,
                signer_accounts=[self.OWNER_SCRIPT_HASH],
                expected_result_type=bool)
        auth_events = engine.get_events('Authorized')

        # check if the event was triggered and the address was authorized
        self.assertEqual(0, auth_events[0].arguments[1])
        self.assertEqual(1, auth_events[0].arguments[2])

        # now deauthorize the address
        self.run_smart_contract(engine, self.CONTRACT_PATH_NEF, 'setAuthorizedAddress', 
                self.OTHER_ACCOUNT_1, False,
                signer_accounts=[self.OWNER_SCRIPT_HASH],
                expected_result_type=bool)
        auth_events = engine.get_events('Authorized')
        # check if the event was triggered and the address was authorized
        self.assertEqual(0, auth_events[1].arguments[1])
        self.assertEqual(0, auth_events[1].arguments[2])

    def test_nep11_pause(self):
        engine = self.prepare_testengine()
        engine.add_contract(self.CONTRACT_PATH_NEF.replace('.py', '.nef'))
        aux_path = self.get_contract_path('test_native', 'auxiliary_contract.py')
        output, manifest = self.compile_and_save(self.CONTRACT_PATH_NEF.replace('.nef', '.py'))
        nep11_address = hash160(output)
        print(to_hex_str(nep11_address))
        output, manifest = self.compile_and_save(aux_path)
        aux_address = hash160(output)
        print(to_hex_str(aux_address))

        # add some gas for fees
        add_amount = 10 * 10 ** 8
        engine.add_gas(aux_address, add_amount)

        # pause contract
        fee = self.run_smart_contract(engine, self.CONTRACT_PATH_NEF, 'updatePause', True,
                signer_accounts=[self.OWNER_SCRIPT_HASH],
                expected_result_type=int)

        # should fail because contract is paused
        with self.assertRaises(TestExecutionException, msg=self.ASSERT_RESULTED_FALSE_MSG):
            token = self.run_smart_contract(engine, self.CONTRACT_PATH_NEF, 'mint', 
                    aux_address, self.TOKEN_META, self.LOCK_CONTENT, self.ROYALTIES,
                    signer_accounts=[aux_address],
                    expected_result_type=bytes)

        # unpause contract
        fee = self.run_smart_contract(engine, self.CONTRACT_PATH_NEF, 'updatePause', False,
                signer_accounts=[self.OWNER_SCRIPT_HASH],
                expected_result_type=bytes)

        # mint
        token = self.run_smart_contract(engine, self.CONTRACT_PATH_NEF, 'mint', 
            aux_address, self.TOKEN_META, self.LOCK_CONTENT, self.ROYALTIES,
            signer_accounts=[aux_address],
            expected_result_type=bytes)
        self.print_notif(engine.notifications)

    def test_nep11_mint(self):
        engine = self.prepare_testengine()
        engine.add_contract(self.CONTRACT_PATH_NEF.replace('.py', '.nef'))
        aux_path = self.get_contract_path('test_native', 'auxiliary_contract.py')
        output, manifest = self.compile_and_save(self.CONTRACT_PATH_NEF.replace('.nef', '.py'))
        nep11_address = hash160(output)
        print(to_hex_str(nep11_address))
        output, manifest = self.compile_and_save(aux_path)
        aux_address = hash160(output)
        print(to_hex_str(aux_address))

        # add some gas for fees
        add_amount = 10 * 10 ** 8
        engine.add_gas(aux_address, add_amount)

        # should fail because royalties are bogus
        with self.assertRaises(TestExecutionException, msg=self.ASSERT_RESULTED_FALSE_MSG):
            token = self.run_smart_contract(engine, self.CONTRACT_PATH_NEF, 'mint', 
                    aux_address, self.TOKEN_META, self.LOCK_CONTENT, self.ROYALTIES_BOGUS,
                    signer_accounts=[aux_address],
                    expected_result_type=bytes)

        # should succeed now that account has enough fees
        token = self.run_smart_contract(engine, self.CONTRACT_PATH_NEF, 'mint', 
                aux_address, self.TOKEN_META, self.LOCK_CONTENT, self.ROYALTIES,
                signer_accounts=[aux_address],
                expected_result_type=bytes)

        print("get props now: ")
        properties = self.run_smart_contract(engine, self.CONTRACT_PATH_NEF, 'properties', token, expected_result_type=ByteString)
        print("props: " + str(properties))
        royalties = self.run_smart_contract(engine, self.CONTRACT_PATH_NEF, 'getRoyalties', token, expected_result_type=ByteString)
        print("royalties: " + str(royalties))
        royaltiesStandard = self.run_smart_contract(engine, self.CONTRACT_PATH_NEF, 'royaltyInfo', token, GAS_SCRIPT, 1_00000000, expected_result_type=ByteString)
        print("royaltiesStandard: " + str(royaltiesStandard))

        print('non existing props:')
        with self.assertRaises(TestExecutionException, msg='An unhandled exception was thrown. Unable to parse metadata'):
            properties = self.run_smart_contract(engine, self.CONTRACT_PATH_NEF, 'properties',
                    bytes('thisisanonexistingtoken', 'utf-8'), expected_result_type=ByteString)
        print("props: " + str(properties))

        # check balances after
        nep11_amount_after = self.run_smart_contract(engine, GAS_SCRIPT, 'balanceOf', nep11_address)
        gas_aux_after = self.run_smart_contract(engine, GAS_SCRIPT, 'balanceOf', aux_address)
        nep11_balance_after = self.run_smart_contract(engine, self.CONTRACT_PATH_NEF, 'balanceOf', aux_address)
        nep11_supply_after = self.run_smart_contract(engine, self.CONTRACT_PATH_NEF, 'totalSupply')
        self.assertEqual(1, nep11_supply_after)
        self.print_notif(engine.notifications)


    def test_nep11_transfer(self):
        engine = self.prepare_testengine()
        engine.add_contract(self.CONTRACT_PATH_NEF.replace('.py', '.nef'))
        aux_path = self.get_contract_path('test_native', 'auxiliary_contract.py')
        output, manifest = self.compile_and_save(self.CONTRACT_PATH_NEF.replace('.nef', '.py'))
        nep11_address = hash160(output)
        print(to_hex_str(nep11_address))
        output, manifest = self.compile_and_save(aux_path)
        aux_address = hash160(output)
        print(to_hex_str(aux_address))

        # add some gas for fees
        add_amount = 10 * 10 ** 8
        engine.add_gas(aux_address, add_amount)

        # mint
        token = self.run_smart_contract(engine, self.CONTRACT_PATH_NEF, 'mint', 
                aux_address, self.TOKEN_META, self.LOCK_CONTENT, self.ROYALTIES,
                signer_accounts=[aux_address],
                expected_result_type=bytes)
        properties = self.run_smart_contract(engine, self.CONTRACT_PATH_NEF, 'properties', token)

        # check balances after
        nep11_amount_after = self.run_smart_contract(engine, GAS_SCRIPT, 'balanceOf', nep11_address)
        gas_aux_after = self.run_smart_contract(engine, GAS_SCRIPT, 'balanceOf', aux_address)
        nep11_balance_after = self.run_smart_contract(engine, self.CONTRACT_PATH_NEF, 'balanceOf', aux_address)
        nep11_supply_after = self.run_smart_contract(engine, self.CONTRACT_PATH_NEF, 'totalSupply')
        self.assertEqual(1, nep11_supply_after)

        # check owner before
        nep11_owner_of_before = self.run_smart_contract(engine, self.CONTRACT_PATH_NEF, 'ownerOf', token)

        # transfer
        result = self.run_smart_contract(engine, self.CONTRACT_PATH_NEF, 'transfer', 
                self.OTHER_ACCOUNT_1, token, None,
                signer_accounts=[aux_address],
                expected_result_type=bool)
        self.assertEqual(True, result)

        # check owner after
        nep11_owner_of_after = self.run_smart_contract(engine, self.CONTRACT_PATH_NEF, 'ownerOf', token)
        self.assertEqual(nep11_owner_of_after, self.OTHER_ACCOUNT_1)

        # check balances after
        nep11_balance_after_transfer = self.run_smart_contract(engine, self.CONTRACT_PATH_NEF, 'balanceOf', aux_address)
        nep11_supply_after_transfer = self.run_smart_contract(engine, self.CONTRACT_PATH_NEF, 'totalSupply')
        self.assertEqual(0, nep11_balance_after_transfer)
        self.assertEqual(1, nep11_supply_after_transfer)

        # try to transfer non existing token id
        with self.assertRaises(TestExecutionException, msg=self.ASSERT_RESULTED_FALSE_MSG):
            result = self.run_smart_contract(engine, self.CONTRACT_PATH_NEF, 'transfer', 
                    self.OTHER_ACCOUNT_1, bytes('thisisanonexistingtoken', 'utf-8'), None,
                    signer_accounts=[aux_address],
                    expected_result_type=bool)

        self.print_notif(engine.notifications)

    def test_nep11_burn(self):
        engine = self.prepare_testengine()
        engine.add_contract(self.CONTRACT_PATH_NEF.replace('.py', '.nef'))
        aux_path = self.get_contract_path('test_native', 'auxiliary_contract.py')
        output, manifest = self.compile_and_save(self.CONTRACT_PATH_NEF.replace('.nef', '.py'))
        nep11_address = hash160(output)
        output, manifest = self.compile_and_save(aux_path)
        aux_address = hash160(output)

        # add some gas for fees
        add_amount = 10 * 10 ** 8
        engine.add_gas(aux_address, add_amount)

        # mint
        token = self.run_smart_contract(engine, self.CONTRACT_PATH_NEF, 'mint', 
                aux_address, self.TOKEN_META, self.LOCK_CONTENT, self.ROYALTIES,
                signer_accounts=[aux_address],
                expected_result_type=bytes)

        # burn
        burn = self.run_smart_contract(engine, self.CONTRACT_PATH_NEF, 'burn', token,
                signer_accounts=[aux_address],
                expected_result_type=bool)

        # check balances after
        nep11_balance_after = self.run_smart_contract(engine, self.CONTRACT_PATH_NEF, 'balanceOf', aux_address)
        self.assertEqual(0, nep11_balance_after)
        nep11_supply_after = self.run_smart_contract(engine, self.CONTRACT_PATH_NEF, 'totalSupply')
        self.assertEqual(0, nep11_supply_after)
        self.print_notif(engine.notifications)

    def test_nep11_onNEP11Payment(self):
        engine = self.prepare_testengine()
        engine.add_contract(self.CONTRACT_PATH_NEF.replace('.py', '.nef'))
        aux_path = self.get_contract_path('test_native', 'auxiliary_contract.py')
        output, manifest = self.compile_and_save(self.CONTRACT_PATH_NEF.replace('.nef', '.py'))
        nep11_address = hash160(output)
        print(to_hex_str(nep11_address))
        output, manifest = self.compile_and_save(aux_path)
        aux_address = hash160(output)
        print(to_hex_str(aux_address))

        # add some gas for fees
        add_amount = 10 * 10 ** 8
        engine.add_gas(self.OTHER_ACCOUNT_1, add_amount)

        # mint
        token = self.run_smart_contract(engine, self.CONTRACT_PATH_NEF, 'mint', 
            self.OTHER_ACCOUNT_1, self.TOKEN_META, self.LOCK_CONTENT, self.ROYALTIES,
            signer_accounts=[self.OTHER_ACCOUNT_1],
            expected_result_type=bytes)

        # the smart contract will abort if any address calls the NEP11 onPayment method
        with self.assertRaises(TestExecutionException, msg=self.ABORTED_CONTRACT_MSG):
            result = self.run_smart_contract(engine, self.CONTRACT_PATH_NEF, 'onNEP11Payment', 
                self.OTHER_ACCOUNT_1, 1, token, None,
                signer_accounts=[self.OTHER_ACCOUNT_1],
                expected_result_type=bool)
