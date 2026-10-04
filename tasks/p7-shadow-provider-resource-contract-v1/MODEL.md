# Exact installed candidate

Alias: hermes-candidate-granite41-30b-q3km-64k, local manifest tag latest. Parent granite4.1:30b-q3_K_M. Both manifests reference the same model digest sha256:dc70d78a721ea39c14c42d44539904e6211e8f6a1fd20902ae7160946df7bccd (13,956,539,616 bytes). All five alias-referenced blobs were streamed read-only and their size/SHA-256 verified, including the model weights; none was loaded.

Config records model_family=granite, model_type=28.9B (the marketed 30B candidate), file_type=Q3_K_M, model_format=gguf. Parameter blob b13b467a485cf95db562958b3d1d8ea251867eb7bda8115bf37a5ee85ab77f7a is exactly {"num_ctx":64000}. Preserve 64000, not an assumed 65536. Historical C5 runtime-summary.json agrees. Inventory JSON preserves exact manifest and config values/hashes. No pull, replacement, quantization change or benchmark.
