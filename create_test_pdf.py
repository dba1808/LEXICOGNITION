"""
Generate a sample test PDF for the AI Viva Voce Examiner
"""
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch
from pathlib import Path

def create_sample_pdf():
    """Create a sample research paper PDF about Transformers"""
    
    output_path = Path(__file__).parent / "test_papers" / "transformer_research.pdf"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=20
    )
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12
    )
    body_style = styles['Normal']
    
    content = []
    
    # Title
    content.append(Paragraph("Attention Is All You Need: A Study of Transformer Architecture", title_style))
    content.append(Paragraph("<i>A Research Paper for Viva Examination Testing</i>", styles['Italic']))
    content.append(Spacer(1, 0.3*inch))
    
    # Abstract
    content.append(Paragraph("Abstract", heading_style))
    content.append(Paragraph(
        "The Transformer architecture has revolutionized natural language processing by introducing "
        "a mechanism called self-attention that allows the model to weigh the importance of different "
        "parts of the input sequence when processing each element. Unlike recurrent neural networks (RNNs) "
        "and convolutional neural networks (CNNs), Transformers process all positions in parallel, "
        "making them significantly more efficient for training on modern hardware. This paper examines "
        "the key components of the Transformer architecture, including multi-head attention, positional "
        "encoding, and the encoder-decoder structure.",
        body_style
    ))
    content.append(Spacer(1, 0.2*inch))
    
    # Introduction
    content.append(Paragraph("1. Introduction", heading_style))
    content.append(Paragraph(
        "Sequence transduction models have traditionally relied on recurrent neural networks, particularly "
        "Long Short-Term Memory (LSTM) and Gated Recurrent Units (GRU). These models process sequences "
        "element by element, maintaining a hidden state that captures information from previous positions. "
        "However, this sequential nature creates a fundamental bottleneck: the computation cannot be "
        "parallelized across positions within a sequence, leading to slow training times especially "
        "for long sequences. The Transformer architecture addresses this limitation by dispensing with "
        "recurrence entirely, instead relying solely on attention mechanisms to capture dependencies "
        "between input and output positions.",
        body_style
    ))
    content.append(Spacer(1, 0.2*inch))
    
    # Self-Attention
    content.append(Paragraph("2. Self-Attention Mechanism", heading_style))
    content.append(Paragraph(
        "The core innovation of the Transformer is the self-attention mechanism, also known as "
        "scaled dot-product attention. For each position in the input sequence, self-attention "
        "computes a weighted sum of all positions, where the weights are determined by the "
        "compatibility between positions. This is achieved through three learned linear projections: "
        "Query (Q), Key (K), and Value (V). The attention weights are computed as the softmax of "
        "the dot product between queries and keys, scaled by the square root of the key dimension "
        "to prevent the dot products from becoming too large. Mathematically, this is expressed as: "
        "Attention(Q, K, V) = softmax(QK^T / sqrt(d_k)) * V. This mechanism allows each position to "
        "attend to all other positions, capturing long-range dependencies that are difficult for "
        "RNNs to learn.",
        body_style
    ))
    content.append(Spacer(1, 0.2*inch))
    
    # Multi-Head Attention
    content.append(Paragraph("3. Multi-Head Attention", heading_style))
    content.append(Paragraph(
        "Rather than performing a single attention function, the Transformer uses multi-head attention, "
        "which runs multiple attention operations in parallel. Each head uses different learned "
        "projections for Q, K, and V, allowing the model to jointly attend to information from "
        "different representation subspaces. The outputs of all heads are concatenated and linearly "
        "projected to produce the final output. This mechanism allows the model to capture different "
        "types of relationships between positions. For example, one head might focus on syntactic "
        "relationships while another captures semantic similarities. The original Transformer uses "
        "8 attention heads, each with dimension d_k = d_v = d_model/8 = 64.",
        body_style
    ))
    content.append(Spacer(1, 0.2*inch))
    
    # Positional Encoding
    content.append(Paragraph("4. Positional Encoding", heading_style))
    content.append(Paragraph(
        "Since the Transformer contains no recurrence or convolution, it has no inherent notion of "
        "position or order in the sequence. To address this, positional encodings are added to the "
        "input embeddings at the bottom of the encoder and decoder stacks. The original Transformer "
        "uses sinusoidal functions of different frequencies: PE(pos, 2i) = sin(pos/10000^(2i/d_model)) "
        "and PE(pos, 2i+1) = cos(pos/10000^(2i/d_model)). These functions were chosen because they "
        "allow the model to easily learn to attend by relative positions, since PE(pos+k) can be "
        "represented as a linear function of PE(pos). Alternative approaches include learned "
        "positional embeddings, which achieve similar results but lack the ability to extrapolate "
        "to sequence lengths longer than those seen during training.",
        body_style
    ))
    content.append(Spacer(1, 0.2*inch))
    
    # Encoder-Decoder
    content.append(Paragraph("5. Encoder-Decoder Architecture", heading_style))
    content.append(Paragraph(
        "The Transformer follows an encoder-decoder architecture commonly used in sequence-to-sequence "
        "models. The encoder maps an input sequence of symbol representations to a sequence of "
        "continuous representations. The decoder then generates an output sequence one element at a "
        "time, consuming the previously generated symbols as additional input. The encoder consists "
        "of a stack of 6 identical layers, each containing two sub-layers: a multi-head self-attention "
        "mechanism and a position-wise fully connected feed-forward network. Residual connections and "
        "layer normalization are applied around each sub-layer. The decoder is similar but includes "
        "a third sub-layer that performs multi-head attention over the encoder output. The self-attention "
        "in the decoder is masked to prevent positions from attending to subsequent positions.",
        body_style
    ))
    content.append(Spacer(1, 0.2*inch))
    
    # Feed-Forward Networks
    content.append(Paragraph("6. Position-wise Feed-Forward Networks", heading_style))
    content.append(Paragraph(
        "In addition to attention sub-layers, each layer in the encoder and decoder contains a fully "
        "connected feed-forward network, applied to each position separately and identically. This "
        "consists of two linear transformations with a ReLU activation in between: FFN(x) = max(0, xW1 + b1)W2 + b2. "
        "The dimensionality of the inner layer is typically larger than the model dimension, with the "
        "original Transformer using d_ff = 2048 compared to d_model = 512. This allows the network to "
        "learn complex transformations at each position while keeping the computational cost manageable.",
        body_style
    ))
    content.append(Spacer(1, 0.2*inch))
    
    # Training
    content.append(Paragraph("7. Training and Optimization", heading_style))
    content.append(Paragraph(
        "The Transformer is trained using the Adam optimizer with a custom learning rate schedule that "
        "increases linearly for a warmup period and then decreases proportionally to the inverse square "
        "root of the step number. This schedule was found to be crucial for stable training. Additionally, "
        "dropout is applied to the output of each sub-layer and to the attention weights, with the "
        "original implementation using a dropout rate of 0.1. Label smoothing is also employed during "
        "training, which hurts perplexity but improves accuracy and BLEU score on machine translation tasks.",
        body_style
    ))
    content.append(Spacer(1, 0.2*inch))
    
    # Results
    content.append(Paragraph("8. Results and Impact", heading_style))
    content.append(Paragraph(
        "The Transformer achieved state-of-the-art results on machine translation benchmarks, reaching "
        "28.4 BLEU on the WMT 2014 English-to-German task and 41.0 BLEU on English-to-French, surpassing "
        "all previously published models. Importantly, training required significantly less time than "
        "recurrent models. The architecture has since become the foundation for large language models "
        "like BERT, GPT, T5, and many others. These models have achieved remarkable results across a "
        "wide range of NLP tasks including question answering, sentiment analysis, named entity recognition, "
        "and text generation. The attention mechanism has also been adapted for computer vision (Vision "
        "Transformer), speech recognition, and multimodal learning.",
        body_style
    ))
    content.append(Spacer(1, 0.2*inch))
    
    # Conclusion
    content.append(Paragraph("9. Conclusion", heading_style))
    content.append(Paragraph(
        "The Transformer architecture represents a paradigm shift in sequence modeling, demonstrating "
        "that attention mechanisms alone are sufficient to achieve state-of-the-art results without "
        "recurrence or convolution. The ability to capture long-range dependencies, combined with "
        "efficient parallel computation, has made Transformers the dominant architecture in modern "
        "deep learning. Future research directions include improving the efficiency of attention for "
        "very long sequences, understanding the representations learned by Transformers, and extending "
        "the architecture to new domains and modalities.",
        body_style
    ))
    
    # Build PDF
    doc.build(content)
    print(f"✅ Created sample PDF: {output_path}")
    return output_path


if __name__ == "__main__":
    try:
        from reportlab.lib.pagesizes import letter
        create_sample_pdf()
    except ImportError:
        print("ReportLab not installed. Install with: pip install reportlab")
        print("Creating a text file instead...")
        
        # Create a simple text file as fallback
        output_path = Path(__file__).parent / "test_papers" / "transformer_research.txt"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            f.write("""
ATTENTION IS ALL YOU NEED: A STUDY OF TRANSFORMER ARCHITECTURE
A Research Paper for Viva Examination Testing

ABSTRACT
The Transformer architecture has revolutionized natural language processing by introducing 
a mechanism called self-attention that allows the model to weigh the importance of different 
parts of the input sequence when processing each element.

1. SELF-ATTENTION MECHANISM
The core innovation is the self-attention mechanism using Query (Q), Key (K), and Value (V) projections.
Attention(Q, K, V) = softmax(QK^T / sqrt(d_k)) * V

2. MULTI-HEAD ATTENTION
Uses multiple attention heads to capture different types of relationships.

3. POSITIONAL ENCODING
Sinusoidal functions encode position information since Transformers have no inherent sequence order.

4. ENCODER-DECODER ARCHITECTURE
The encoder maps input to continuous representations, the decoder generates output autoregressively.
""")
        print(f"✅ Created sample text file: {output_path}")
