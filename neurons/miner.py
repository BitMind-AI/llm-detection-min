# The MIT License (MIT)
# Copyright © 2023 Nikita Dilman

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of
# the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

import time
import typing
import bittensor as bt

import random

# Bittensor Miner Template:
import detection

from detection.utils.weight_version import is_version_in_range

# import base miner class which takes care of most of the boilerplate
from detection.base.miner import BaseMinerNeuron
from miners.ppl_model import PPLModel

from transformers.utils import logging as hf_logging

from miners.deberta_classifier import DebertaClassifier

hf_logging.set_verbosity(40)


class Miner(BaseMinerNeuron):
    """
    Your miner neuron class. You should use this class to define your miner's behavior. In particular, you should replace the forward function with your own logic. You may also want to override the blacklist and priority functions according to your needs.

    This class inherits from the BaseMinerNeuron class, which in turn inherits from BaseNeuron. The BaseNeuron class takes care of routine tasks such as setting up wallet, subtensor, metagraph, logging directory, parsing config, etc. You can override any of the methods in BaseNeuron if you need to customize the behavior.

    This class provides reasonable default behavior for a miner such as blacklisting unrecognized hotkeys, prioritizing requests based on stake, and forwarding requests to the forward function. If you need to define custom
    """

    def __init__(self, config=None):
        super(Miner, self).__init__(config=config)
        
        # No model loading in this dummy implementation
        bt.logging.info("Initializing dummy miner without loading any models")
        
        # We still call load_state to maintain compatibility with the base class
        self.load_state()
        
        bt.logging.info("Dummy miner initialized successfully")

    async def forward(
        self, synapse: detection.protocol.TextSynapse
    ) -> detection.protocol.TextSynapse:
        """
        Minimal implementation that returns a dummy response in the correct format.
        
        Args:
            synapse (detection.protocol.TextSynapse): The synapse object containing the 'texts' data.

        Returns:
            detection.protocol.TextSynapse: The synapse object with dummy 'predictions'.
        """
        # Log the start time
        start_time = time.time()
        
        # Get the input texts
        input_data = synapse.texts
        bt.logging.info(f"Amount of texts received: {len(input_data)}")
        
        # Create dummy predictions (0 for human, 1 for AI)
        # Each text gets a random prediction (0 or 1)
        # Each word in the text gets the same prediction
        dummy_preds = [random.randint(0, 1) for _ in range(len(input_data))]
        
        # Format predictions as required: list of lists where each inner list
        # has the same prediction repeated for each word in the text
        formatted_preds = [[pred] * len(text.split()) for pred, text in zip(dummy_preds, input_data)]
        
        bt.logging.info(f"Generated dummy predictions in {int(time.time() - start_time)}s")
        
        # Set the predictions in the synapse
        synapse.predictions = formatted_preds
        
        return synapse


    async def blacklist(
        self, synapse: detection.protocol.TextSynapse
    ) -> typing.Tuple[bool, str]:
        """
        Determines whether an incoming request should be blacklisted and thus ignored. Your implementation should
        define the logic for blacklisting requests based on your needs and desired security parameters.

        Blacklist runs before the synapse data has been deserialized (i.e. before synapse.data is available).
        The synapse is instead contructed via the headers of the request. It is important to blacklist
        requests before they are deserialized to avoid wasting resources on requests that will be ignored.

        Args:
            synapse (detection.protocol.TextSynapse): A synapse object constructed from the headers of the incoming request.

        Returns:
            Tuple[bool, str]: A tuple containing a boolean indicating whether the synapse's hotkey is blacklisted,
                            and a string providing the reason for the decision.

        This function is a security measure to prevent resource wastage on undesired requests. It should be enhanced
        to include checks against the metagraph for entity registration, validator status, and sufficient stake
        before deserialization of synapse data to minimize processing overhead.

        Example blacklist logic:
        - Reject if the hotkey is not a registered entity within the metagraph.
        - Consider blacklisting entities that are not validators or have insufficient stake.

        In practice it would be wise to blacklist requests from entities that are not validators, or do not have
        enough stake. This can be checked via metagraph.S and metagraph.validator_permit. You can always attain
        the uid of the sender via a metagraph.hotkeys.index( synapse.dendrite.hotkey ) call.

        Otherwise, allow the request to be processed further.
        """
        # if synapse.dendrite.hotkey not in self.metagraph.hotkeys:
        #     # Ignore requests from unrecognized entities.
        #     bt.logging.trace(
        #         f"Blacklisting unrecognized hotkey {synapse.dendrite.hotkey}"
        #     )
        #     self.blacklist_hotkeys.add(synapse.dendrite.hotkey)
        #     bt.logging.info(f'List of blacklisted hotkeys: {self.blacklist_hotkeys}')
        #     return True, "Unrecognized hotkey"

        # uid = self.metagraph.hotkeys.index(synapse.dendrite.hotkey)

        # stake = self.metagraph.S[uid].item()
        # if stake < self.config.blacklist.minimum_stake_requirement:
        #     self.blacklist_hotkeys.add(synapse.dendrite.hotkey)
        #     bt.logging.info(f'List of blacklisted hotkeys: {self.blacklist_hotkeys}')
        #     return True, "pubkey stake below min_allowed_stake"

        # bt.logging.trace(
        #     f"Not Blacklisting recognized hotkey {synapse.dendrite.hotkey}"
        # )
        return False, "Hotkey recognized!"

    async def priority(self, synapse: detection.protocol.TextSynapse) -> float:
        """
        The priority function determines the order in which requests are handled. More valuable or higher-priority
        requests are processed before others. You should design your own priority mechanism with care.

        This implementation assigns priority to incoming requests based on the calling entity's stake in the metagraph.

        Args:
            synapse (detection.protocol.TextSynapse): The synapse object that contains metadata about the incoming request.

        Returns:
            float: A priority score derived from the stake of the calling entity.

        Miners may recieve messages from multiple entities at once. This function determines which request should be
        processed first. Higher values indicate that the request should be processed first. Lower values indicate
        that the request should be processed later.

        Example priority logic:
        - A higher stake results in a higher priority value.
        """
        caller_uid = self.metagraph.hotkeys.index(
            synapse.dendrite.hotkey
        )  # Get the caller index.
        prirority = float(
            self.metagraph.S[caller_uid]
        )  # Return the stake as the priority.
        bt.logging.trace(
            f"Prioritizing {synapse.dendrite.hotkey} with value: ", prirority
        )
        return prirority


# This is the main function, which runs the miner.
if __name__ == "__main__":
    with Miner() as miner:
        while True:
            bt.logging.info("Miner running...", time.time())
            time.sleep(30)
