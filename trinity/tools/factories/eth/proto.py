from p2p.abc import HandshakerAPI
from trinity.protocol.eth.proto import ETHProtocolV63

try:
    import factory
except ImportError:
    raise ImportError("The p2p.tools.factories module requires the `factory_boy` library.")

from typing import (
    cast,
    AsyncContextManager,
    Tuple,
    Any,
)

from lahja import EndpointAPI

from cancel_token import CancelToken

from eth_typing import BlockNumber

from eth_keys import keys
from eth.constants import GENESIS_BLOCK_NUMBER

from p2p import kademlia
from p2p.tools.factories import PeerPairFactory

from trinity.protocol.common.context import ChainContext

from trinity.protocol.eth.handshaker import ETHHandshaker
from trinity.protocol.eth.peer import ETHPeer, ETHPeerFactory

from trinity.tools.factories.chain_context import ChainContextFactory

from .payloads import StatusPayloadFactory


class ETHHandshakerFactory(factory.Factory):
    class Meta:
        model = ETHHandshaker

    handshake_params = factory.SubFactory(StatusPayloadFactory)


class ETHV63Peer(ETHPeer):
    supported_sub_protocols = (ETHProtocolV63,)  # type: ignore


class ETHV63PeerFactory(ETHPeerFactory):
    peer_class = ETHV63Peer

    async def get_handshakers(self) -> Tuple[HandshakerAPI[Any], ...]:
        return tuple(
            shaker for shaker in await super().get_handshakers()
            # mypy doesn't know these have a `handshake_params` property
            if shaker.handshake_params.version == ETHProtocolV63.version  # type: ignore
        )


def ETHV63PeerPairFactory(*,
                          alice_peer_context: ChainContext = None,
                          alice_remote: kademlia.Node = None,
                          alice_private_key: keys.PrivateKey = None,
                          alice_client_version: str = 'alice',
                          bob_peer_context: ChainContext = None,
                          bob_remote: kademlia.Node = None,
                          bob_private_key: keys.PrivateKey = None,
                          bob_client_version: str = 'bob',
                          cancel_token: CancelToken = None,
                          event_bus: EndpointAPI = None,
                          ) -> AsyncContextManager[Tuple[ETHPeer, ETHPeer]]:
    if alice_peer_context is None:
        alice_peer_context = ChainContextFactory()

    if bob_peer_context is None:
        alice_genesis = alice_peer_context.headerdb.get_canonical_block_header_by_number(
            BlockNumber(GENESIS_BLOCK_NUMBER),
        )
        bob_peer_context = ChainContextFactory(
            headerdb__genesis_params={'timestamp': alice_genesis.timestamp},
        )

    return cast(AsyncContextManager[Tuple[ETHPeer, ETHPeer]], PeerPairFactory(
        alice_peer_context=alice_peer_context,
        alice_peer_factory_class=ETHV63PeerFactory,
        bob_peer_context=bob_peer_context,
        bob_peer_factory_class=ETHV63PeerFactory,
        alice_remote=alice_remote,
        alice_private_key=alice_private_key,
        alice_client_version=alice_client_version,
        bob_remote=bob_remote,
        bob_private_key=bob_private_key,
        bob_client_version=bob_client_version,
        cancel_token=cancel_token,
        event_bus=event_bus,
    ))


def ETHPeerPairFactory(*,
                       alice_peer_context: ChainContext = None,
                       alice_remote: kademlia.Node = None,
                       alice_private_key: keys.PrivateKey = None,
                       alice_client_version: str = 'alice',
                       bob_peer_context: ChainContext = None,
                       bob_remote: kademlia.Node = None,
                       bob_private_key: keys.PrivateKey = None,
                       bob_client_version: str = 'bob',
                       cancel_token: CancelToken = None,
                       event_bus: EndpointAPI = None,
                       ) -> AsyncContextManager[Tuple[ETHPeer, ETHPeer]]:
    if alice_peer_context is None:
        alice_peer_context = ChainContextFactory()

    if bob_peer_context is None:
        alice_genesis = alice_peer_context.headerdb.get_canonical_block_header_by_number(
            BlockNumber(GENESIS_BLOCK_NUMBER),
        )
        bob_peer_context = ChainContextFactory(
            headerdb__genesis_params={'timestamp': alice_genesis.timestamp},
        )

    return cast(AsyncContextManager[Tuple[ETHPeer, ETHPeer]], PeerPairFactory(
        alice_peer_context=alice_peer_context,
        alice_peer_factory_class=ETHPeerFactory,
        bob_peer_context=bob_peer_context,
        bob_peer_factory_class=ETHPeerFactory,
        alice_remote=alice_remote,
        alice_private_key=alice_private_key,
        alice_client_version=alice_client_version,
        bob_remote=bob_remote,
        bob_private_key=bob_private_key,
        bob_client_version=bob_client_version,
        cancel_token=cancel_token,
        event_bus=event_bus,
    ))
